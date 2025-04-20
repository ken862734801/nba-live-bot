import os
import asyncio

import twitchio
from twitchio import eventsub
from twitchio.ext import commands
from supabase import create_client, Client
from commands.command import CommandComponent
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
BOT_ID = os.getenv("TWITCH_BOT_ID")

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

SB: Client = create_client(URL, KEY)

class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=BOT_ID,
            prefix="!",
        )

    async def setup_hook(self) -> None:

        await self.add_component(CommandComponent(self))
        await self.load_tokens()

        response = SB.table("channels").select("broadcaster_user_id").execute()
        channels = [record["broadcaster_user_id"] for record in response.data]

        for channel in channels:
            subscription = eventsub.ChatMessageSubscription(broadcaster_user_id=channel, user_id=self.bot_id)
            await self.subscribe_websocket(payload=subscription)

    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
            response = await super().add_token(token, refresh)

            await SB.table("application_tokens") \
                .upsert({
                    "user_id": response.user_id,
                    "access_token": token,
                    "refresh_token": refresh
                }, on_conflict="user_id") \
                .execute()
                
            return response

    async def load_tokens(self) -> None:
        response = SB.table("application_tokens").select("*").execute()
        for row in response.data:
            await super().add_token(row["access_token"], row["refresh_token"])

    async def event_ready(self) -> None:
        print("Successfully connected to Twitch!")
        
def main() -> None:
    async def runner() -> None:
        bot = Bot()
        await bot.start()
    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping bot.")

if __name__ == "__main__":
    main()
