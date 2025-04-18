from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamgamelog
from nba_api.live.nba.endpoints import scoreboard, boxscore

class NBAService:

    @staticmethod
    def _all_teams():
        return teams.get_teams()
    
    @staticmethod
    def _get_team_info(name: str) -> dict | None:
        n = name.lower()
        for t in NBAService._all_teams():
            if (
                n == t["full_name"].lower() or
                n == t["nickname"].lower()  or
                n == t["abbreviation"].lower()
            ):
                return t
        return None
    
    @staticmethod
    def get_team_record(name: str) -> str:
        data = NBAService._get_team_info(name)
        if not data:
            return f"Team not found: {name}."
        
        try:
            df = teamgamelog.TeamGameLog(team_id=data["id"]).get_data_frames()[0]
            wins, losses = df.iloc[0]["W"], df.iloc[0]["L"]
            return f"The {data['full_name']} are {wins} - {losses}."
        except Exception as e:
            return f"Error fetching record: {e}"
    
    @staticmethod
    def get_game_score(name: str) -> str:
        data = NBAService._get_team_info(name)
        if not data:
            return f"Team not found: {name}."
        
        try:
            games = scoreboard.ScoreBoard().get_dict()["scoreboard"]["games"]
            for g in games:
                h, a = g["homeTeam"], g["awayTeam"]
                if h["teamId"] == data["id"] or a["teamId"] == data["id"]:
                    away_nm = f"{a['teamCity']} {a['teamName']}"
                    home_nm = f"{h['teamCity']} {h['teamName']}"
                    b = boxscore.BoxScore(game_id=g["gameId"]).get_dict()["game"]
                    status = b["gameStatusText"]
                    return f"{away_nm} {b['awayTeam']['score']} - {home_nm} {b['homeTeam']['score']} ({status})"
            return f"The {data['full_name']} are not currently playing."
        except Exception as e:
            return f"Error fetching score: {e}"
