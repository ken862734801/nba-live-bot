import os
import asyncio
import twitchio
from twitchio import eventsub
from twitchio.ext import commands
from supabase import create_client, Client
from commands.command import CommandComponent
from dotenv import load_dotenv
from realtime import AsyncRealtimeClient

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
BOT_ID = os.getenv("TWITCH_BOT_ID")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SB: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
WS_URL = SUPABASE_URL.replace("https", "wss") + "/realtime/v1"


class Bot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            bot_id=BOT_ID,
            prefix="!",
        )
        self.realtime_client = AsyncRealtimeClient(WS_URL, SUPABASE_KEY, auto_reconnect=True)

    async def setup_hook(self) -> None:
        await self.add_component(CommandComponent(self))
        await self.load_tokens()
        await self.init_subscription()
        await self.start_realtime_listener()

    async def init_subscription(self) -> None:
        response = SB.table("channels").select("broadcaster_user_id").eq("is_active", True).execute()
        channels = [record["broadcaster_user_id"] for record in response.data]

        for channel in channels:
            subscription = eventsub.ChatMessageSubscription(broadcaster_user_id=channel, user_id=self.bot_id)
            await self.subscribe_websocket(payload=subscription)
            print(f"📡 Initial subscription to channel {channel}")

    async def handle_channel_update(self, payload):
        data = payload.get("data", {})
        new_row = data.get("record", {})

        user_id = new_row.get("broadcaster_user_id")
        is_active = new_row.get("is_active")

        print(f"🔄 UPDATE — broadcaster_user_id: {user_id}, is_active: {is_active}")

        if is_active:
            print(f"✅ Subscribing to {user_id}")
            subscription = eventsub.ChatMessageSubscription(broadcaster_user_id=user_id, user_id=self.bot_id)
            await self.subscribe_websocket(payload=subscription)
        else:
            print(f"❌ Unsubscribing from {user_id}")
            await self.unsubscribe_websocket(broadcaster_user_id=user_id)

    async def handle_channel_insert(self, payload):
        data = payload.get("data", {})
        new_row = data.get("record", {})

        user_id = new_row.get("broadcaster_user_id")
        is_active = new_row.get("is_active")

        print(f"🆕 INSERT — broadcaster_user_id: {user_id}, is_active: {is_active}")

        if is_active:
            print(f"✅ Subscribing to {user_id}")
            subscription = eventsub.ChatMessageSubscription(broadcaster_user_id=user_id, user_id=self.bot_id)
            await self.subscribe_websocket(payload=subscription)
        else:
            print(f"⚠️ Not subscribing to {user_id} because is_active is False")

    async def start_realtime_listener(self):
        await self.realtime_client.connect()
        channel = self.realtime_client.channel("realtime:public:channels")

        # Register both INSERT and UPDATE handlers
        channel.on_postgres_changes(
            event="UPDATE",
            schema="public",
            table="channels",
            callback=lambda payload: asyncio.create_task(self.handle_channel_update(payload))
        )

        channel.on_postgres_changes(
            event="INSERT",
            schema="public",
            table="channels",
            callback=lambda payload: asyncio.create_task(self.handle_channel_insert(payload))
        )

        # Subscribe once AFTER registering all handlers
        await channel.subscribe()

        print("📶 Supabase Realtime listener subscribed to INSERT + UPDATE")
        asyncio.create_task(self._realtime_loop())


    async def _realtime_loop(self):
        while True:
            await asyncio.sleep(1)

    async def unsubscribe_websocket(self, broadcaster_user_id: str):
        subscriptions = self.websocket_subscriptions()
        for sub_id, sub in subscriptions.items():
            if sub.condition.get("broadcaster_user_id") == broadcaster_user_id:
                await self.delete_websocket_subscription(sub_id)  # 👈 use the key here
                print(f"🧹 Successfully unsubscribed from {broadcaster_user_id}")
                return


    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        response = await super().add_token(token, refresh)

        await SB.table("application_tokens").upsert({
            "user_id": response.user_id,
            "access_token": token,
            "refresh_token": refresh
        }, on_conflict="user_id").execute()

        return response

    async def load_tokens(self) -> None:
        response = SB.table("application_tokens").select("*").execute()
        for row in response.data:
            await super().add_token(row["access_token"], row["refresh_token"])

    async def event_ready(self) -> None:
        print("✅ Successfully connected to Twitch!")

def main() -> None:
    async def runner() -> None:
        bot = Bot()
        await bot.start()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        print("👋 Stopping bot.")

if __name__ == "__main__":
    main()
