import asyncio
import logging
import os

from supabase import create_client, Client
from twitchio.ext import commands

from api.nba import NBAClient
from config import Config
from managers.command import CommandManager
from managers.database import DatabaseManager
from managers.proxy import ProxyManager
from managers.websocket import WebSocketManager

logging.basicConfig(level=logging.ERROR)

logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            client_id=Config.CLIENT_ID,
            client_secret=Config.CLIENT_SECRET,
            bot_id=Config.BOT_ID,
            prefix="!",
        )
        self.supabase_client = create_client(
            Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.websocket_manager = WebSocketManager(self)
        self.database_manager = DatabaseManager(
            self.supabase_client, self.websocket_manager)
        self.proxy_manager = ProxyManager(Config.PROXY_LIST.split(","))
        self.nba_client = NBAClient(self.proxy_manager)

    async def setup_hook(self) -> None:
        await self.add_component(CommandManager(self, self.nba_client))
        await self.load_tokens()
        await self.database_manager.seed()
        await self.database_manager.listen()

    async def load_tokens(self) -> None:
        await super().add_token(Config.TWITCH_ACCESS_TOKEN, Config.TWITCH_REFRESH_TOKEN),

    async def event_ready(self) -> None:
        print(f"{Config.BOT_USERNAME} is ONLINE and READY to receive commands.")


def main() -> None:
    async def runner() -> None:
        bot = Bot()
        try:
            await bot.start()
        finally:
            await bot.database_manager.close()
    asyncio.run(runner())


if __name__ == "__main__":
    main()
