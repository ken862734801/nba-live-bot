from nba_api_client import get_score

def score_command(team_name: str) -> str:
    return get_score(team_name)