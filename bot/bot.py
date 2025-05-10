import os
import asyncio
import logging

from supabase import create_client, Client
from twitchio import eventsub
from twitchio.ext import commands

from config import Config
from commands import CommandComponent
from services.realtime_listener import RealtimeListener
from services.twitch.eventsub import subscribe_to_websocket

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")


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
        self.realtime_listener = RealtimeListener(self)

    async def setup_hook(self) -> None:
        await self.add_component(CommandComponent(self))
        await self.load_tokens()
        await self.join_all()
        await self.realtime_listener.start()

    async def join_all(self) -> None:
        rows = self.supabase_client.table("channels").select(
            "broadcaster_user_id").eq("is_active", True).execute().data
        for row in rows:
            broadcaster_user_id = row.get("broadcaster_user_id")
            if broadcaster_user_id:
                await subscribe_to_websocket(self, broadcaster_user_id)
                logging.info(
                    "Subscribed to chat for broadcaster ID: %s", broadcaster_user_id)
            else:
                logging.warning("Row missing 'broadcaster_user_id': %s", row)

    async def load_tokens(self) -> None:
        await super().add_token(Config.TWITCH_ACCESS_TOKEN, Config.TWITCH_REFRESH_TOKEN),

    async def event_ready(self) -> None:
        logging.info(
            f"{Config.BOT_USERNAME} is ONLINE and READY to receive commands")


def main() -> None:
    async def runner() -> None:
        bot = Bot()
        try:
            await bot.start()
        finally:
            await bot.realtime_listener.client.close()
    print("ENV TOKEN: ", os.getenv("TWITCH_ACCESS_TOKEN"))
    print("CONFIG TOKEN: ", Config.TWITCH_ACCESS_TOKEN)
    asyncio.run(runner())


if __name__ == "__main__":
    main()
