from nba_api.live.nba.endpoints import boxscore, scoreboard
from nba_api.stats.static import teams

def get_score(team_name: str) -> str:
    """
    Fetches the current score and game status for a given NBA team.

    Args:
        team_name (str): The name of the NBA team to fetch the score for.

    Returns:
        str: A formatted string containing the game's score and status if the team is playing,
             or a message indicating that the team is not currently playing.
    """
    try:
        all_teams = teams.get_teams()
        matched_team = next(
            (team for team in all_teams if team_name.lower() in team["full_name"].lower()),
            None
        )
        if not matched_team:
            return "Team not found."
        
        full_team_name = matched_team["full_name"]

        games = scoreboard.ScoreBoard().get_dict()["scoreboard"]["games"]

        for game in games:
            game_id = game["gameId"]

            home = game["homeTeam"]
            away = game["awayTeam"]

            full_home = f"{home['teamCity']} {home['teamName']}"
            full_away = f"{away['teamCity']} {away['teamName']}"

            if team_name.lower() in full_home.lower() or team_name.lower() in home["teamName"].lower():
                return format_score(game_id, full_home, full_away)
            elif team_name.lower() in full_away.lower() or team_name.lower() in away["teamName"].lower():
                return format_score(game_id, full_home, full_away)

        return f"The {full_team_name} are not currently playing."

    except Exception as e:
        return f"Error fetching boxscore: {e}"

def format_score(game_id: str, full_home: str, full_away: str) -> str:
    """
    Formats the score and game status for a given game.

    Args:
        game_id (str): The unique identifier for the game.
        full_home (str): The full name of the home team (e.g., "Los Angeles Lakers").
        full_away (str): The full name of the away team (e.g., "Golden State Warriors").

    Returns:
        str: A formatted string containing the score and game status.
    """
    data = boxscore.BoxScore(game_id=game_id).get_dict()

    home_team = data["game"]["homeTeam"]
    away_team = data["game"]["awayTeam"]
    status = data["game"]["gameStatusText"]

    home_score = home_team["score"]
    away_score = away_team["score"]

    return f"{full_away} {away_score} - {full_home} {home_score} ({status})"
