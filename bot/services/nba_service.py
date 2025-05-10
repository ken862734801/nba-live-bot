import datetime
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playercareerstats, teamgamelog
from nba_api.live.nba.endpoints import scoreboard, boxscore


class NBAService:

    @staticmethod
    def _all_teams():
        return teams.get_teams()

    @staticmethod
    def _get_player_data(name):
        name_lower = name.lower().strip()
        for player in players.get_players():
            if player["full_name"].lower() == name_lower:
                return player
        return None

    @staticmethod
    def _get_team_data(name):
        name_lower = name.lower().strip()
        for team in NBAService._all_teams():
            if (
                name_lower == team["full_name"].lower() or
                name_lower == team["nickname"].lower() or
                name_lower == team["abbreviation"].lower()
            ):
                return team
        return None

    @staticmethod
    def get_game_score(name):
        data = NBAService._get_team_data(name)
        if not data:
            return f"Team not found: {name}"
        try:
            games = scoreboard.ScoreBoard().get_dict()["scoreboard"]["games"]
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
            return f'Error: {e}'

    @staticmethod
    def get_player_career_averages(player_name: str) -> str:
        name_lower = player_name.lower().strip()
        player = NBAService._get_player_data(name_lower)
        if not player:
            return f"Player not found: {player_name}"
        try:
            career = playercareerstats.PlayerCareerStats(
                player_id=player["id"])
            df = career.get_data_frames()[0]
            if df.empty:
                return f"No career statistics found for {player_name}"
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
            return f"Error: {e}"

    @staticmethod
    def get_player_statline(player_name: str) -> str:
        try:
            name_key = player_name.lower().strip()
            games = scoreboard.ScoreBoard().get_dict()["scoreboard"]["games"]

            for game in games:
                game_id = game["gameId"]

                try:
                    box = boxscore.BoxScore(game_id=game_id)
                    data = box.get_dict()["game"]
                except Exception as e:
                    continue

                for side in ("homeTeam", "awayTeam"):
                    for player in data[side]["players"]:
                        if player["name"].lower() == name_key:
                            if "statistics" not in player:
                                continue

                            s = player["statistics"]
                            pts = s["points"]
                            reb = s["reboundsTotal"]
                            ast = s["assists"]
                            stl = s["steals"]
                            blk = s["blocks"]
                            tov = s["turnovers"]
                            raw_min = s["minutes"]
                            minp = int(raw_min.split("PT")[1].split("M")[0])

                            fgm = s["fieldGoalsMade"]
                            fga = s["fieldGoalsAttempted"]
                            fg3m = s["threePointersMade"]
                            fg3a = s["threePointersAttempted"]
                            ftm = s["freeThrowsMade"]
                            fta = s["freeThrowsAttempted"]

                            return (
                                f"{player['name']}: "
                                f"{pts} PTS ({fgm}/{fga} FG, {fg3m}/{fg3a} 3PT, {ftm}/{fta} FT), "
                                f"{reb} REB, {ast} AST, {stl} STL, {blk} BLK, {tov} TO "
                                f"in {minp} MIN"
                            )

            return f"{player_name} is not currently playing."
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def get_team_record(name):
        data = NBAService._get_team_data(name)
        if not data:
            return f"Team not found: {name}"

        try:
            df = teamgamelog.TeamGameLog(
                team_id=data["id"]).get_data_frames()[0]
            wins, losses = df.iloc[0]["W"], df.iloc[0]["L"]
            return f"The {data['full_name']} are {wins} - {losses}"

        except Exception as e:
            return f'Error: {e}'

    @staticmethod
    def get_schedule() -> str:
        games = scoreboard.ScoreBoard().get_dict()["scoreboard"]["games"]
        if not games:
            return "No games scheduled."

        dt_ests = []
        matchups = []
        for g in games:
            away = g["awayTeam"]["teamTricode"]
            home = g["homeTeam"]["teamTricode"]
            utc_str = g.get("gameTimeUTC", "")
            try:
                dt_utc = datetime.datetime.strptime(
                    utc_str, "%Y-%m-%dT%H:%M:%SZ")
                dt_est = dt_utc - datetime.timedelta(hours=4)
                dt_ests.append(dt_est)
                et_formatted = dt_est.strftime("%I:%M %p EST").lstrip("0")
            except Exception:
                et_formatted = "TBD"
            matchups.append(f"{away} @ {home} ({et_formatted})")

        schedule_date = dt_ests[0].date()
        day = schedule_date.day

        if 11 <= (day % 100) <= 13:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        date_str = f"{schedule_date.strftime('%B')} {day}{suffix}"

        return f"{date_str}: " + ", ".join(matchups)
