import os
import asyncio
import logging

import twitchio
from twitchio import eventsub
from twitchio.ext import commands

from config import Config
from commands.command import CommandComponent
from services.realtime import RealtimeListener
from services.supabase import get_supabase_client
from services.eventsub import subscribe_to_websocket

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            client_id=Config.CLIENT_ID,
            client_secret=Config.CLIENT_SECRET,
            bot_id=Config.BOT_ID,
            prefix="!",
        )
        self.supabase_client = get_supabase_client()
        self.realtime_listener = RealtimeListener(self)

    async def setup_hook(self) -> None:
        await self.add_component(CommandComponent(self))
        await self.load_tokens()
        await self.join_active_channels()
        await self.realtime_listener.start()

    async def join_active_channels(self) -> None:
        rows = self.supabase_client.table("channels").select("broadcaster_user_id").eq("is_active", True).execute().data
        for row in rows:
            broadcaster_user_id = row.get("broadcaster_user_id")
            if broadcaster_user_id:
                await subscribe_to_websocket(self, broadcaster_user_id)
                logging.info("Subscribed to chat for broadcaster ID: %s", broadcaster_user_id)
            else:
                logging.warning("Row missing 'broadcaster_user_id': %s", row)

    async def load_tokens(self) -> None:
        await super().add_token(Config.TWITCH_ACCESS_TOKEN, Config.TWITCH_REFRESH_TOKEN),

    async def event_ready(self) -> None:
        logging.info("The bot has connected to Twitch")

def main() -> None:
    async def runner() -> None:
        bot = Bot()
        try:
            await bot.start()
        finally:
            await bot.realtime_listener.client.close()
    asyncio.run(runner())

if __name__ == "__main__":
    main()
