import logging

from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, teamgamelog
from nba_api.live.nba.endpoints import scoreboard, boxscore

from utils.schedule_formatter import format_schedule

logger = logging.getLogger(__name__)


class NBAClient:
    @staticmethod
    def _get_all_players():
        return players.get_players()

    @staticmethod
    def _get_all_teams():
        return teams.get_teams()

    @staticmethod
    def _get_player_data(name):
        for player in NBAClient._get_all_players():
            if player["full_name"].lower() == name.lower():
                return player
        logger.warning(f"Player not found: {name}")
        return None

    @staticmethod
    def _get_team_data(name):
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
    def get_game_score(name):
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
    def get_player_career(name):
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
    def get_player_statline(name):
        try:
            _scoreboard = scoreboard.ScoreBoard()
            games = _scoreboard.get_dict()["scoreboard"]["games"]

            for game in games:
                game_id = game["gameId"]

                try:
                    _boxscore = boxscore.BoxScore(game_id=game_id)
                    data = _boxscore.get_dict()["game"]
                except Exception as e:
                    logger.warning(f"Error fetching boxscore: {e}")
                    continue
                for team in ("homeTeam", "awayTeam"):
                    for player in data[team]["players"]:
                        if player["name"].lower() == name.lower():
                            statistics = player["statistics"]
                            points = statistics["points"]
                            rebounds = statistics["rebounds"]
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
                                f"{rebounds} REB, {assists} AST, "
                                f"in {formatted_minutes} MIN "
                            )
        except Exception as e:
            logger.error("Error fetching player statline: {e}")
            return f'Something went wrong. Try again later.'

    @staticmethod
    def get_team_record(name):
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
            return f'Something went wrong. Try again later.'

    @staticmethod
    def get_schedule():
        _scoreboard = scoreboard.ScoreBoard()
        games = _scoreboard.get_dict()["scoreboard"]["games"]
        return format_schedule(games)
