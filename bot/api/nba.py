import logging
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, teamgamelog
from nba_api.live.nba.endpoints import scoreboard, boxscore
from utils.schedule_formatter import format_schedule

logger = logging.getLogger(__name__)


class NBAClient:
    @staticmethod
    def _get_all_players():
        """Get all NBA players.

        Returns:
            list: A list of dictionaries containing player information.
        """
        return players.get_players()

    @staticmethod
    def _get_all_teams():
        """Get all NBA teams.

        Returns:
            list: A list of dictionaries containing team information.
        """
        return teams.get_teams()

    @staticmethod
    def _get_player_data(name: str) -> str | None:
        """Get data for a specific player.

        Args:
            name (str): The name of the player.

        Returns:
            dict | None: A dictionary containing player information, or None if the player is not found.
        """
        for player in NBAClient._get_all_players():
            if player["full_name"].lower() == name.lower():
                return player
        logger.warning(f"Player not found: {name}")
        return None

    @staticmethod
    def _get_team_data(name: str) -> str | None:
        """Get data for a specific team.

        Args:
            name (str): The name of the team.

        Returns:
            dict | None: A dictionary containing team information, or None if the team is not found.
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

    @staticmethod
    def get_game_score(name: str) -> str:
        """Get the score of a specific team's game.

        Args:
            name (str): The name of the team.

        Returns:
            str: The game score in the format "Away Team Score - Home Team Score (Status)".
        """
        data = NBAClient._get_team_data(name)
        if not data:
            return f"Team not found: {name}"
        try:
            _scoreboard = scoreboard.ScoreBoard()
            games = _scoreboard.get_dict()["scoreboard"]["games"]
            for game in games:
                home_team, away_team = game["homeTeam"], game["awayTeam"]
                if home_team["teamId"] == data["id"] or away_team["teamId"] == data["id"]:
                    away_name = f"{away_team['teamCity']} {away_team['teamName']}"
                    home_name = f"{home_team['teamCity']} {home_team['teamName']}"
                    box_score = boxscore.BoxScore(
                        game_id=game["gameId"]).get_dict()["game"]
                    status = box_score["gameStatusText"]
                    return f"{away_name} {box_score['awayTeam']['score']} - {home_name} {box_score['homeTeam']['score']} ({status})"
            return f"The {data['full_name']} are not currently playing."
        except Exception as e:
            logger.error(f"Error fetching game score: {e}")
            return f'Something went wrong. Try again later.'

    @staticmethod
    def get_player_career(name: str) -> str:
        """Get the career statistics of a specific player.

        Args:
            name (str): The name of the player.

        Returns:
            str: The player's career statistics in the format "Player Name: Average Points PTS, Average Rebounds REB, Average Assists AST, Average Field Goal Percentage%".
        """
        player = NBAClient._get_player_data(name)
        if not player:
            return f"Player not found: {name}"
        try:
            career = playercareerstats.PlayerCareerStats(
                player_id=player["id"]
            )
            df = career.get_data_frames()[0]
            if df.empty:
                logger.warning(f"No career data found for {name}")
                return "Something went wrong. Try again later."
            games_played = df["GP"].sum()
            total_points = df["PTS"].sum()
            total_rebounds = df["REB"].sum()
            total_assists = df["AST"].sum()
            total_field_goals_attempted = df["FGA"].sum()
            total_field_goals_made = df["FGM"].sum()

            average_points = round(total_points / games_played, 1)
            average_rebounds = round(total_rebounds / games_played, 1)
            average_assists = round(total_assists / games_played, 1)
            average_field_goal_percentage = round(
                (total_field_goals_made / total_field_goals_attempted) * 100, 1
            )
            return f"{player['full_name']}: {average_points} PTS, {average_rebounds} REB, {average_assists} AST, {average_field_goal_percentage}%"
        except Exception as e:
            logger.error(f"Error fetching player career: {e}")
            return f'Something went wrong. Try again later.'

    @staticmethod
    def get_player_statline(name: str) -> str:
        """Get the statline of a specific player in the current game.

        Args:
            name (str): The name of the player.

        Returns:
            str: The player's statline in the format "Player Name: Points PTS (Field Goals Made/Attempted FG, Three Pointers Made/Attempted 3PT, Free Throws Made/Attempted FT), Rebounds REB, Assists AST, Steals STL, Blocks BLK, Turnovers TO in Minutes MIN".
        """
        try:
            _scoreboard = scoreboard.ScoreBoard()
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

    @staticmethod
    def get_team_record(name: str) -> str:
        """Get the win-loss record of a specific team.

        Args:
            name (str): The name of the team.

        Returns:
            str: The team's win-loss record in the format "The Team Name are W - L".
        """
        data = NBAClient._get_team_data(name)
        if not data:
            return f"Team not found: {name}"
        try:
            _teamgamelog = teamgamelog.TeamGameLog(team_id=data["id"])
            df = _teamgamelog.get_data_frames()[0]
            w, l = df.iloc[0]["W"], df.iloc[0]["L"]
            return f"The {data['full_name']} are {w} - {l}"
        except Exception as e:
            logger.error(f"Error fetching team record: {e}")
            return 'Something went wrong. Try again later.'

    @staticmethod
    def get_schedule() -> str:
        """Get the NBA game schedule.

        Returns:
            str: The formatted game schedule.
        """
        _scoreboard = scoreboard.ScoreBoard()
        games = _scoreboard.get_dict()["scoreboard"]["games"]
        return format_schedule(games)
