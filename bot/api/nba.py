import datetime
import logging

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, teamgamelog
from nba_api.live.nba.endpoints import scoreboard, boxscore

from managers.proxy import ProxyManager
from managers.redis import RedisManager
from utils.schedule_formatter import format_schedule

logger = logging.getLogger(__name__)


class NBAClient:
    """
    Wrapper around the nba_api library to fetch NBA data (scores, stats, schedules),
    using a ProxyManager to rotate proxies on each request.
    """

    def __init__(self, proxy_manager: ProxyManager, redis_manager: RedisManager):
        """
        Initialize the NBAClient.

        Args:
            proxy_manager (ProxyManager): Manages which proxy to use for outgoing requests.
        """
        self.proxy_manager = proxy_manager
        self.redis = redis_manager

    @staticmethod
    def _get_all_players() -> list[dict]:
        """
        Retrieve the full list of NBA players from the static endpoint.

        Returns:
            list[dict]: A list of player metadata dicts.
        """
        return players.get_players()

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

        Args:
            name (str): The player's full name.

        Returns:
            dict | None: The matching player dict, or None if not found.
        """
        for player in NBAClient._get_all_players():
            if player["full_name"].lower() == name.lower():
                return player
        logger.warning(f"Player not found: {name}")
        return None

    @staticmethod
    def _get_team_data(name: str) -> dict | None:
        """
        Look up a team by full name, nickname, or abbreviation (case-insensitive).

        Args:
            name (str): The team's full name, nickname, or abbreviation.

        Returns:
            dict | None: The matching team dict, or None if not found.
        """
        for team in NBAClient._get_all_teams():
            if (
                name.lower() == team["full_name"].lower() or
                name.lower() == team["nickname"].lower() or
                name.lower() == team["abbreviation"].lower()
            ):
                return team
        logger.warning(f"Team not found: {name}")
        return None

    async def get_game_score(self, name: str) -> str:
        """
        Fetch the current game score for the given team.

        Args:
            name (str): The team's name, nickname, or abbreviation.

        Returns:
            str: A formatted score string, or an error/message if not playing or not found.
        """
        data = NBAClient._get_team_data(name)
        if not data:
            return f"Team not found: {name}"

        proxy = await self.proxy_manager.get_proxy()
        try:
            sb = scoreboard.ScoreBoard(proxy=proxy).get_dict()[
                "scoreboard"]["games"]
            for game in sb:
                home, away = game["homeTeam"], game["awayTeam"]
                if data["id"] in (home["teamId"], away["teamId"]):
                    away_name = f"{away['teamCity']} {away['teamName']}"
                    home_name = f"{home['teamCity']} {home['teamName']}"
                    box = boxscore.BoxScore(
                        game_id=game["gameId"]).get_dict()["game"]
                    status = box["gameStatusText"]
                    return (
                        f"{away_name} {box['awayTeam']['score']} - "
                        f"{home_name} {box['homeTeam']['score']} ({status})"
                    )
            return f"The {data['full_name']} are not currently playing."
        except Exception as e:
            logger.error(f"Error fetching game score: {e}")
            return "Something went wrong. Try again later."

    async def get_player_career(self, name: str) -> str:
        """
        Compute and return a player's career averages.

        Args:
            name (str): The player's full name.

        Returns:
            str: A summary of career PTS, REB, AST, FG% or an error/message if not found.
        """
        cache_key = f"career:{name.lower()}"
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {name}")
            return cached

        player = NBAClient._get_player_data(name)
        if not player:
            return f"Player not found: {name}"

        proxy = await self.proxy_manager.get_proxy()
        try:
            career = playercareerstats.PlayerCareerStats(
                player_id=player["id"],
                proxy=proxy,
            ).get_data_frames()[0]
            if career.empty:
                logger.warning(f"No career data for {name}")
                return "Something went wrong. Try again later."

            gp = career["GP"].sum()
            pts = career["PTS"].sum()
            reb = career["REB"].sum()
            ast = career["AST"].sum()
            fgm = career["FGM"].sum()
            fga = career["FGA"].sum()

            avg_pts = round(pts / gp, 1)
            avg_reb = round(reb / gp, 1)
            avg_ast = round(ast / gp, 1)
            fg_pct = round((fgm / fga) * 100, 1) if fga else 0.0

            result = (
                f"{player['full_name']}: {avg_pts} PTS, "
                f"{avg_reb} REB, {avg_ast} AST, {fg_pct}% FG"
            )
            await self.redis.set(cache_key, result, expire_seconds=3600)
            return result
        except Exception as e:
            logger.error(f"Error fetching player career: {e}")
            return "Something went wrong. Try again later."

    async def get_player_statline(self, name: str) -> str:
        """
        Fetch a player's box-score stat line from any game happening right now.

        Args:
            name (str): The player's name (case-insensitive).

        Returns:
            str: A formatted stat line or a not-playing/message if not found.
        """
        proxy = await self.proxy_manager.get_proxy()
        try:
            _scoreboard = scoreboard.ScoreBoard(proxy=proxy)
            games = _scoreboard.get_dict()["scoreboard"]["games"]

            for game in games:
                game_id = game["gameId"]

                try:
                    box = boxscore.BoxScore(game_id=game_id)
                    data = box.get_dict()["game"]
                except Exception as e:
                    continue

                for side in ("homeTeam", "awayTeam"):
                    for player in data[side]["players"]:
                        if player["name"].lower() == name.lower():
                            if "statistics" not in player:
                                continue

                            statistics = player["statistics"]
                            points = statistics["points"]
                            rebounds = statistics["reboundsTotal"]
                            assists = statistics["assists"]
                            steals = statistics["steals"]
                            blocks = statistics["blocks"]
                            turnovers = statistics["turnovers"]
                            minutes = statistics["minutes"]
                            formatted_minutes = int(
                                minutes.split("PT")[1].split("M")[0])

                            field_goals_made = statistics["fieldGoalsMade"]
                            field_goals_attempted = statistics["fieldGoalsAttempted"]
                            three_pointers_made = statistics["threePointersMade"]
                            three_pointers_attempted = statistics["threePointersAttempted"]
                            free_throws_made = statistics["freeThrowsMade"]
                            free_throws_attempted = statistics["freeThrowsAttempted"]

                            return (
                                f"{player['name']}: "
                                f"{points} PTS ({field_goals_made}/{field_goals_attempted} FG, {three_pointers_made}/{three_pointers_attempted} 3PT, {free_throws_made}/{free_throws_attempted} FT), "
                                f"{rebounds} REB, {assists} AST, {steals} STL, {blocks} BLK, {turnovers} TO "
                                f"in {formatted_minutes} MIN"
                            )
            logger.warning(f"Player not found: {name}")
            return f"{name} is not currently playing."
        except Exception as e:
            logger.error(f"Error fetching player statline: {e}")
            return 'Something went wrong. Try again later.'

    async def get_team_record(self, name: str) -> str:
        """
        Retrieve the current win-loss record for a team.

        Args:
            name (str): The team's full name, nickname, or abbreviation.

        Returns:
            str: A formatted record string or an error/message if not found.
        """
        data = NBAClient._get_team_data(name)
        if not data:
            return f"Team not found: {name}"

        cache_key = f"record:{data['id']}"
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {name.lower()}.")
            return cached

        proxy = await self.proxy_manager.get_proxy()
        try:
            df = teamgamelog.TeamGameLog(
                team_id=data["id"], proxy=proxy).get_data_frames()[0]
            w, l = df.iloc[0]["W"], df.iloc[0]["L"]
            result = f"The {data['full_name']} are {w} - {l}"
            await self.redis.set(cache_key, result, expire_seconds=3600)
            return result
        except Exception as e:
            logger.error(f"Error fetching team record: {e}")
            return "Something went wrong. Try again later."

    async def get_schedule(self) -> str:
        """
        Fetch and format today's NBA schedule.

        Returns:
            str: A schedule, or "No games scheduled."
        """
        cache_key = "schedule"
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {cache_key}.")
            return cached

        proxy = await self.proxy_manager.get_proxy()
        games = scoreboard.ScoreBoard(proxy=proxy).get_dict()[
            "scoreboard"]["games"]
        result = format_schedule(games)
        await self.redis.set(cache_key, result, expire_seconds=3600)
        return result
