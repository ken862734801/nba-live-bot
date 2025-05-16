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
    This class also caches results in Redis to reduce API calls and improve performance.
    """

    def __init__(self, proxy_manager: ProxyManager, redis_manager: RedisManager):
        """
        Initialize the NBAClient.

        Args:
            proxy_manager (ProxyManager): Manages which proxy to use for outgoing requests.
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

        Args:
            name (str): The player's full name.

        Returns:
            dict | None: The matching player dict, or None if not found.
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

        Args:
            name (str): The team's full name, nickname, or abbreviation.

        Returns:
            dict | None: The matching team dict, or None if not found.
        """
        for team in NBAClient._get_all_teams():
            name_lower = name.strip().lower()
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
        Fetch the current game score for the given team, retrying up to 3 proxies
        if an API call fails, and cache the result in Redis for 1 hour.
        """

        data = NBAClient._get_team_data(name)
        if not data:
            return f"Team not found: {name}"

        for attempt in range(3):
            proxy = await self.proxy_manager.get_proxy()
            try:
                games = (
                    scoreboard.ScoreBoard(proxy=proxy)
                              .get_dict()["scoreboard"]["games"]
                )
                break
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt+1}/3 failed with proxy={proxy!r}: {e}")
        else:
            logger.error("All proxy retries failed for get_game_score")
            return "Something went wrong. Try again later."

        for game in games:
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

    async def get_player_career(self, name: str) -> str:
        """
        Compute and return a player's career averages, retrying up to 3 proxies
        if an API call fails (no caching).
        """

        player = NBAClient._get_player_data(name)
        if not player:
            return f"Player not found: {name}"

        for attempt in range(3):
            proxy = await self.proxy_manager.get_proxy()
            try:
                career_df = (
                    playercareerstats.PlayerCareerStats(
                        player_id=player["id"],
                        proxy=proxy,
                    )
                    .get_data_frames()[0]
                )
                break
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt+1}/3 failed with proxy={proxy!r}: {e}")
        else:
            logger.error("All proxy retries failed for get_player_career")
            return "Something went wrong. Try again later."

        if career_df.empty:
            logger.warning(f"No career data for {name}")
            return "Something went wrong. Try again later."

        gp = career_df["GP"].sum()
        pts = career_df["PTS"].sum()
        reb = career_df["REB"].sum()
        ast = career_df["AST"].sum()
        fgm = career_df["FGM"].sum()
        fga = career_df["FGA"].sum()

        avg_pts = round(pts / gp, 1)
        avg_reb = round(reb / gp, 1)
        avg_ast = round(ast / gp, 1)
        fg_pct = round((fgm / fga) * 100, 1) if fga else 0.0

        return (
            f"{player['full_name']}: "
            f"{avg_pts} PTS, {avg_reb} REB, {avg_ast} AST, {fg_pct}% FG"
        )


    async def get_player_statline(self, name: str) -> str:
        """
        Fetch a player's box-score stat line from any game happening right now,
        retrying up to 3 times with fresh proxies if we hit an exception.
        """
        max_retries = 3
        name_lower = name.strip().lower()

        for attempt in range(1, max_retries + 1):
            proxy = await self.proxy_manager.get_proxy()
            try:
                _scoreboard = scoreboard.ScoreBoard(proxy=proxy)
                games = _scoreboard.get_dict()["scoreboard"]["games"]

                for game in games:
                    game_id = game["gameId"]

                    try:
                        box = boxscore.BoxScore(game_id=game_id)
                        data = box.get_dict()["game"]
                    except Exception:
                        continue

                    for side in ("homeTeam", "awayTeam"):
                        for player in data[side]["players"]:
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
                            mins = int(stats["minutes"].split(
                                "PT")[1].split("M")[0])

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

            except Exception as e:
                logger.error(
                    f"[Attempt {attempt}/{max_retries}] Error fetching statline for {name}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)
                else:
                    return "Something went wrong. Try again later."

    async def get_team_record(self, name: str) -> str:
        """
        Retrieve the current win-loss record for a team, retrying up to 3 times on failure.

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
            logger.info(f"Cache hit for {name} season record.")
            return cached

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            proxy = await self.proxy_manager.get_proxy()
            try:
                df = teamgamelog.TeamGameLog(
                    team_id=data["id"],
                    proxy=proxy
                ).get_data_frames()[0]

                w, l = df.iloc[0]["W"], df.iloc[0]["L"]
                result = f"The {data['full_name']} are {w} - {l}"
                await self.redis.set(cache_key, result, expire_seconds=3600)
                return result

            except Exception as e:
                logger.error(f"[Attempt {attempt}/{max_retries}] Error fetching team record for {name}: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)
                else:
                    return "Something went wrong. Try again later."

    async def get_schedule(self) -> str:
        """
        Fetch and format today's NBA schedule, retrying up to 3 times on failure.
        Returns:
            str: A schedule, or "No games scheduled.", or an error message.
        """
        cache_key = "schedule"
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info("Cache hit for today's NBA schedule.")
            return cached

        max_retries = 3
        for attempt in range(1, max_retries + 1):
            proxy = await self.proxy_manager.get_proxy()
            try:
                games = scoreboard.ScoreBoard(proxy=proxy).get_dict()["scoreboard"]["games"]
                result = format_schedule(games)
                await self.redis.set(cache_key, result, expire_seconds=3600)
                return result

            except Exception as e:
                logger.error(f"[Attempt {attempt}/{max_retries}] Error fetching schedule: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)
                else:
                    return "Something went wrong. Try again later."
