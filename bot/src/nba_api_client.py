from nba_api.live.nba.endpoints import boxscore, scoreboard

def get_score(team_name: str) -> str:
    try:
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

        return f"The {team_name} are not currently playing."

    except Exception as e:
        return f"Error fetching boxscore: {e}"


def format_score(game_id: str, full_home: str, full_away: str) -> str:
    data = boxscore.BoxScore(game_id=game_id).get_dict()

    home_team = data["game"]["homeTeam"]
    away_team = data["game"]["awayTeam"]
    status = data["game"]["gameStatusText"]

    home_score = home_team["score"]
    away_score = away_team["score"]

    return f"{full_away} {away_score} - {full_home} {home_score} ({status})"

print(get_score("Bulls"))
