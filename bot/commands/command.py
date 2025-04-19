import asyncio
from services.nba_api_service import NBAService

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self._commands = {}

    def register_command(self, name: str, func):
        self._commands[name] = func

    async def handle(self, user, text):
        if not text.startswith("!"):
            return
        parts = text[1:].split(None, 1)
        name = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        cmd = self._commands.get(name)
        if cmd:
            await cmd(self.bot, args, user)

async def record_command(bot, args, user):
    if not args:
        await bot.send_chat_message(f"@{user} Usage: !record <team>")
        return
    response = NBAService.get_team_record(args)
    await bot.send_chat_message(f"@{user} {response}")

async def score_command(bot, args, user):
    if not args:
        await bot.send_chat_message(f"@{user} Usage: !score <team>")
        return
    response = NBAService.get_game_score(args)
    await bot.send_chat_message(f"@{user} {response}")