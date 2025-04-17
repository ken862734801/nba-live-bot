from nba_api_client import get_score, get_record

COMMANDS = {
    'score': get_score,
    'record': get_record,
}

USAGES = {
    'score': 'Usage: !score <team_name>',
    'record': 'Usage: !record <team_name>',
}

def handle_command(text: str) -> str | None:
    parts = text.lstrip('!').split(' ', 1)
    cmd = parts[0]
    arg = parts[1] if len(parts) > 1 else ''
    func = COMMANDS.get(cmd)
    if not func:
        return None
    if not arg:
        return USAGES.get(cmd, f"Usage: !{cmd} <args>")
    return func(arg)