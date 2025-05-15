import datetime


def _convert_utc_to_est(utc_str: str) -> datetime.datetime | None:
    """
    Parse a UTC timestamp string and convert it to Eastern Standard Time.

    Args:
        utc_str (str): A UTC datetime string in ISO format (e.g., "2025-05-15T19:30:00Z").

    Returns:
        datetime.datetime | None: The corresponding EST datetime (UTC−4), or None if parsing fails.
    """
    try:
        utc_dt = datetime.datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        return utc_dt - datetime.timedelta(hours=4)
    except Exception:
        return None


def _format_time_est(est_dt: datetime.datetime | None) -> str:
    """
    Format an EST datetime as a human-readable time string, or return "TBD" if not provided.

    Args:
        est_dt (datetime.datetime | None): The EST datetime to format.

    Returns:
        str: A string like "7:30 PM EST" (leading zero removed) or "TBD" if est_dt is None.
    """
    if not est_dt:
        return "TBD"
    return est_dt.strftime("%I:%M %p EST").lstrip("0")


def _get_day_suffix(day: int) -> str:
    """
    Determine the English ordinal suffix for a given day of the month.

    Args:
        day (int): The day of the month (1–31).

    Returns:
        str: The ordinal suffix, one of "st", "nd", "rd", or "th".
    """
    if 11 <= (day % 100) <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def format_matchup(game: dict) -> tuple[str, datetime.datetime | None]:
    """
    Build a formatted matchup string and extract its EST datetime.

    Args:
        game (dict): A dictionary representing a game, expected to contain:
                     - "awayTeam": {"teamTricode": str}
                     - "homeTeam": {"teamTricode": str}
                     - "gameTimeUTC": str (ISO timestamp)

    Returns:
        tuple[str, datetime.datetime | None]:
            - A string like "GSW @ LAL (7:30 PM EST)".
            - The EST datetime object, or None if conversion failed.
    """
    away_team = game["awayTeam"]["teamTricode"]
    home_team = game["homeTeam"]["teamTricode"]
    est_dt = _convert_utc_to_est(game.get("gameTimeUTC", ""))
    time_str = _format_time_est(est_dt)
    matchup_string = f"{away_team} @ {home_team} ({time_str})"
    return matchup_string, est_dt


def format_schedule(games: list[dict]) -> str:
    """
    Generate a daily schedule summary string for a list of games.

    Args:
        games (list[dict]): A list of game dictionaries as accepted by format_matchup().

    Returns:
        str: A summary like "May 15th: GSW @ LAL (7:30 PM EST), BOS @ NYK (8:00 PM EST)".
             Returns "No games scheduled." if the list is empty.
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
        first_date = est_dts[0].date()
        day = first_date.day
        suffix = _get_day_suffix(day)
        date_str = f"{first_date.strftime('%B')} {day}{suffix}"
    else:
        date_str = ""

    return f"{date_str}: " + ", ".join(matchups)
