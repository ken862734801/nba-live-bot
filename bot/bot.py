import os
import asyncio
import twitchio

from twitchio import eventsub
from twitchio.ext import commands
from supabase import create_client, Client
from commands.command import CommandComponent
from services.realtime import RealtimeListener
from services.supabase import _get_supabase_client
from services.eventsub import subscribe_to_twitch_chat

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
BOT_ID = os.getenv("TWITCH_BOT_ID")

class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=BOT_ID,
            prefix="!",
        )
        self.sb = _get_supabase_client()
        self.listener = RealtimeListener(self)

    async def setup_hook(self) -> None:
        await self.add_component(CommandComponent(self))
        await self.load_tokens()
        await self.subscribe_to_active_rows()
        await self.listener.start()

    async def subscribe_to_active_rows(self) -> None:
        rows = self.sb.table("channels").select("broadcaster_user_id").eq("is_active", True).execute().data
        for row in rows:
            await subscribe_to_twitch_chat(self, row["broadcaster_user_id"])

    async def add_bot_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        response = await super().add_token(token, refresh)

        await self.sb.table("credentials").upsert({
            "user_id": response.user_id,
            "access_token": token,
            "refresh_token": refresh
        }, on_conflict="user_id").execute()

        return response

    async def load_bot_tokens(self) -> None:
        response = self.sb.table("credentials").select("*").execute()
        for row in response.data:
            await super().add_token(row["access_token"], row["refresh_token"])

    async def event_ready(self) -> None:
        print("Bot is online!")

def main() -> None:
    async def runner() -> None:
        bot = Bot()
        try:
            await bot.start()
        finally:
            await bot.listener.client.close()
    asyncio.run(runner())

if __name__ == "__main__":
    main()
