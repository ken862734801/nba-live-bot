from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog
from nba_api.live.nba.endpoints import scoreboard, boxscore

def _all_teams():
    return teams.get_teams()

def get_team_id(name):
    n = name.lower()
    for t in _all_teams():
        if (
            n in t["full_name"].lower()
            or n in t["nickname"].lower()
            or n in t["abbreviation"].lower()
        ):
            return t["id"]
    return f"Team not found: {name}."

def get_record(name):
    team_id = get_team_id(name)

    try:
        game_log = teamgamelog.TeamGameLog(team_id=team_id)
        game_log_df = game_log.get_data_frames()[0]

        win_count = game_log_df.iloc[0]['W']
        loss_count = game_log_df.iloc[0]['L']

        return f'The {name} are {win_count} - {loss_count}.'
    except Exception as e:
        return f'Error: {e}'

def get_score(name):
    team_id = get_team_id(name)

    full_name = next(
        (t["full_name"] for t in _all_teams() if t["id"] == team_id),
        name
    )

    try:
        games = scoreboard.ScoreBoard().get_dict()["scoreboard"]["games"]
        for g in games:
            home = g["homeTeam"]
            away = g["awayTeam"]

            if home["teamId"] == team_id or away["teamId"] == team_id:
                away_team = f"{away['teamCity']} {away['teamName']}"
                home_team = f"{home['teamCity']} {home['teamName']}"
            
            b = boxscore.BoxScore(game_id=g["gameId"])
            status = b.get_dict()["gameStatusText"]
            away_score = b.get_dict()["homeTeamScore"]
            home_score = b.get_dict()["awayTeamScore"]

            return f"{away_team} {away_home} - {home_team} {home_score} ({status})"

        return f"The {full_name} are not currently playing."
    
    except Exception as e:
        return f"Error fetching score: {e}"

print(get_record("Lakers"))
print(get_score("Lakers"))