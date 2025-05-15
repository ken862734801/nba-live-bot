import datetime


def _convert_utc_to_est(utc_str: str) -> datetime.datetime | None:
    """
    Converts a UTC datetime string to Eastern Standard Time (EST).

    Args:
        utc_str (str): The UTC datetime string in the format "%Y-%m-%dT%H:%M:%SZ".

    Returns:
        datetime.datetime | None: The converted datetime in EST, or None if the conversion fails.
    """
    try:
        utc_dt = datetime.datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        return utc_dt - datetime.timedelta(hours=4)
    except Exception:
        return None


def _format_time_est(est_dt: datetime.datetime | None) -> str:
    """
    Formats the given datetime object in Eastern Standard Time (EST) format.

    Args:
        est_dt (datetime.datetime | None): The datetime object to be formatted.

    Returns:
        str: The formatted time in the format "HH:MM AM/PM EST".
    """
    if not est_dt:
        return "TBD"
    return est_dt.strftime("%I:%M %p EST").lstrip("0")


def _get_day_suffix(day: int) -> str:
    """Return the English ordinal suffix for a given day of month."""
    if 11 <= (day % 100) <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def format_matchup(game: dict) -> tuple[str, datetime.datetime | None]:
    """
    Formats the matchup information for a game.

    Args:
        game (dict): A dictionary containing the game information.

    Returns:
        tuple[str, datetime.datetime | None]: A tuple containing the formatted matchup string and the game time in EST.
    """
    away_team = game["awayTeam"]["teamTricode"]
    home_team = game["homeTeam"]["teamTricode"]
    est_dt = _convert_utc_to_est(game.get("gameTimeUTC", ""))
    time_str = _format_time_est(est_dt)
    matchup_string = f"{away_team} @ {home_team} ({time_str})"
    return matchup_string, est_dt


def format_schedule(games: list[dict]) -> str:
    """
    Given a list of game dicts, return either:
     - "No games scheduled."
     - or "Month D[suffix]: MATCHUP1, MATCHUP2, …"

    Args:
        games (list[dict]): A list of game dictionaries.

    Returns:
        str: The formatted schedule string.
    """
    if not games:
        return "No games scheduled."

    matchups: list[str] = []
    est_dts: list[datetime.datetime] = []

    for game in games:
        text, dt = format_matchup(game)
        matchups.append(text)
        if dt:
            est_dts.append(dt)

    if est_dts:
        schedule_date = est_dts[0].date()
        day = schedule_date.day
        suffix = _get_day_suffix(day)
        date_str = f"{schedule_date.strftime('%B')} {day}{suffix}"
    else:
        date_str = ""

    return f"{date_str}: " + ", ".join(matchups)
