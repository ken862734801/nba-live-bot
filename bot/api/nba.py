import asyncio
import datetime
import logging
import os

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, teamgamelog
from nba_api.live.nba.endpoints import scoreboard, boxscore

from managers.redis import RedisManager
from utils.schedule_formatter import format_schedule

logger = logging.getLogger(__name__)


class NBAClient:
    """
    Wrapper around the nba_api library to fetch NBA data (scores, stats, schedules),
    using a rotating proxy endpoint on every request.
    This class also caches results in Redis to reduce API calls and improve performance.
    """

    def __init__(self, proxy_manager, redis_manager: RedisManager):
        """
        Initialize the NBAClient.

        Args:
            proxy_manager (ProxyManager): Provides the rotating proxy URL.
            redis_manager (RedisManager): Manages Redis cache for storing data.
        """
        self.proxy_manager = proxy_manager
        self.redis = redis_manager

    @staticmethod
    def _get_all_teams() -> list[dict]:
        """
        Retrieve the full list of NBA teams from the static endpoint.
        Returns:
            list[dict]: A list of team metadata dicts.
        """
        return teams.get_teams()

    @staticmethod
    def _get_player_data(name: str) -> dict | None:
        """
        Look up a player by full name (case-insensitive).
        """
        matches = players.find_players_by_full_name(name)
        if matches:
            return matches[0]
        logger.warning(f"Player not found: {name}")
        return None

    @staticmethod
    def _get_team_data(name: str) -> dict | None:
        """
        Look up a team by full name, nickname, or abbreviation (case-insensitive).
        """
        name_lower = name.strip().lower()
        for team in NBAClient._get_all_teams():
            if (
                name_lower == team["full_name"].lower() or
                name_lower == team["nickname"].lower() or
                name_lower == team["abbreviation"].lower()
            ):
                return team
        logger.warning(f"Team not found: {name}")
        return None

    async def get_game_score(self, name: str) -> str:
        """
        Fetch the current game score for the given team, using the rotating proxy.
        Results are not cached.
        """
        data = NBAClient._get_team_data(name)
        if not data:
            return f"Team not found: {name}"

        proxy = await self.proxy_manager.get_proxy()
        games = scoreboard.ScoreBoard(proxy=proxy).get_dict()[
            "scoreboard"]["games"]

        for game in games:
            home, away = game["homeTeam"], game["awayTeam"]
            if data["id"] in (home["teamId"], away["teamId"]):
                box = boxscore.BoxScore(
                    game_id=game["gameId"], proxy=proxy).get_dict()["game"]
                away_name = f"{away['teamCity']} {away['teamName']}"
                home_name = f"{home['teamCity']} {home['teamName']}"
                status = box["gameStatusText"]

                return (
                    f"{away_name} {box['awayTeam']['score']} - "
                    f"{home_name} {box['homeTeam']['score']} ({status})"
                )
        return f"The {data['full_name']} are not currently playing."

    async def get_player_career(self, name: str) -> str:
        """
        Compute and return a player's career averages, using the rotating proxy (no caching).
        """
        player = NBAClient._get_player_data(name)
        if not player:
            return f"Player not found: {name}"

        proxy = await self.proxy_manager.get_proxy()
        career_df = playercareerstats.PlayerCareerStats(
            player_id=player["id"], proxy=proxy
        ).get_data_frames()[0]

        if career_df.empty:
            logger.warning(f"No career data for {name}")
            return "No career data available."

        gp = career_df["GP"].sum()
        pts = career_df["PTS"].sum()
        reb = career_df["REB"].sum()
        ast = career_df["AST"].sum()
        fgm = career_df["FGM"].sum()
        fga = career_df["FGA"].sum()

        avg_pts = round(pts / gp, 1) if gp else 0.0
        avg_reb = round(reb / gp, 1) if gp else 0.0
        avg_ast = round(ast / gp, 1) if gp else 0.0
        fg_pct = round((fgm / fga) * 100, 1) if fga else 0.0

        return (
            f"{player['full_name']}: "
            f"{avg_pts} PTS, {avg_reb} REB, {avg_ast} AST, {fg_pct}% FG"
        )

    async def get_player_statline(self, name: str) -> str:
        """
        Fetch a player's box-score stat line from any live game, using the rotating proxy.
        """
        name_lower = name.strip().lower()
        proxy = await self.proxy_manager.get_proxy()

        games = scoreboard.ScoreBoard(proxy=proxy).get_dict()[
            "scoreboard"]["games"]
        for game in games:
            game_id = game["gameId"]
            box = boxscore.BoxScore(
                game_id=game_id, proxy=proxy).get_dict()["game"]
            for side in ("homeTeam", "awayTeam"):
                for player in box[side]["players"]:
                    if player["name"].lower() != name_lower:
                        continue
                    stats = player.get("statistics")
                    if not stats:
                        continue

                    pts = stats["points"]
                    reb = stats["reboundsTotal"]
                    ast = stats["assists"]
                    stl = stats["steals"]
                    blk = stats["blocks"]
                    tov = stats["turnovers"]
                    mins = int(stats["minutes"].split("PT")[1].split("M")[0])

                    fg_m = stats["fieldGoalsMade"]
                    fg_a = stats["fieldGoalsAttempted"]
                    tp_m = stats["threePointersMade"]
                    tp_a = stats["threePointersAttempted"]
                    ft_m = stats["freeThrowsMade"]
                    ft_a = stats["freeThrowsAttempted"]

                    return (
                        f"{player['name']}: {pts} PTS "
                        f"({fg_m}/{fg_a} FG, {tp_m}/{tp_a} 3PT, {ft_m}/{ft_a} FT), "
                        f"{reb} REB, {ast} AST, {stl} STL, {blk} BLK, {tov} TO "
                        f"in {mins} MIN"
                    )
        logger.warning(f"Player not found: {name}")
        return f"{name} is not currently playing."

    async def get_team_record(self, name: str) -> str:
        """
        Retrieve the current win-loss record for a team, using the rotating proxy.
        """
        data = NBAClient._get_team_data(name)
        if not data:
            return f"Team not found: {name}"

        cache_key = f"record:{data['id']}"
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {name} season record.")
            return cached

        proxy = await self.proxy_manager.get_proxy()
        df = teamgamelog.TeamGameLog(
            team_id=data["id"], proxy=proxy).get_data_frames()[0]
        w, l = df.iloc[0]["W"], df.iloc[0]["L"]
        result = f"The {data['full_name']} are {w} - {l}"
        await self.redis.set(cache_key, result, expire_seconds=3600)
        return result

    async def get_schedule(self) -> str:
        """
        Fetch and format today's NBA schedule, using the rotating proxy.
        Returns:
            str: A schedule, or "No games scheduled."
        """
        cache_key = "schedule"
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info("Cache hit for today's NBA schedule.")
            return cached

        proxy = await self.proxy_manager.get_proxy()
        games = scoreboard.ScoreBoard(proxy=proxy).get_dict()[
            "scoreboard"]["games"]
        result = format_schedule(games)
        await self.redis.set(cache_key, result, expire_seconds=3600)
        return result
