from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog
from nba_api.live.nba.endpoints import scoreboard, boxscore

class NBAService:
    @staticmethod
    def _all_teams():
        return teams.get_teams()
    
    @staticmethod
    def _get_team_info(name):
        name_lower = name.lower()
        for team in NBAService._all_teams():
            if (
                name_lower == team["full_name"].lower() or
                name_lower == team["nickname"].lower()  or
                name_lower == team["abbreviation"].lower()
            ):
                return team
        return None
    
    @staticmethod
    def get_team_record(name):
        data = NBAService._get_team_info(name)
        if not data:
            return f"Team not found: {name}."

        try:
            df = teamgamelog.TeamGameLog(team_id=data["id"]).get_data_frames()[0]
            wins, losses = df.iloc[0]["W"], df.iloc[0]["L"]
            return f"The {data['full_name']} are {wins} - {losses}."

        except Exception as e:
            return f'Error: {e}'
    
    @staticmethod
    def get_game_score(name):
        data = NBAService._get_team_info(name)
        if not data:
            return f"Team not found: {name}."
        try:
            games = scoreboard.ScoreBoard().get_dict()["scoreboard"]["games"]
            for game in games:
                home_team, away_team = game["homeTeam"], game["awayTeam"]
                if home_team["teamId"] == data["id"] or away_team["teamId"] == data["id"]:
                    away_name = f"{away_team['teamCity']} {away_team['teamName']}"
                    home_name = f"{home_team['teamCity']} {home_team['teamName']}"
                    box_score = boxscore.BoxScore(game_id=game["gameId"]).get_dict()["game"]
                    status = box_score["gameStatusText"]
                    return f"{away_name} {box_score['awayTeam']['score']} - {home_name} {box_score['homeTeam']['score']} ({status})"
            return f"The {data['full_name']} are not currently playing."
            
        except Exception as e:
            return f'Error: {e}'
            