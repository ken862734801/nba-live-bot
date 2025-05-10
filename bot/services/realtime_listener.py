import os
import asyncio

from realtime import AsyncRealtimeClient

from config import Config
from services.twitch.eventsub import subscribe_to_websocket, unsubscribe_from_websocket


class RealtimeListener:

    WS_URL = Config.SUPABASE_URL.replace("https", "wss") + "/realtime/v1"

    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncRealtimeClient(
            self.WS_URL, Config.SUPABASE_KEY, auto_reconnect=True)

    async def start(self):
        await self.client.connect()
        channel = self.client.channel("realtime:public:channels")

        channel.on_postgres_changes(event="UPDATE", schema="public", table="channels",
                                    callback=lambda payload: asyncio.create_task(self.on_row_update(payload)))
        channel.on_postgres_changes(event="INSERT", schema="public", table="channels",
                                    callback=lambda payload: asyncio.create_task(self.on_row_insert(payload)))

        await channel.subscribe()

    async def on_row_update(self, payload):
        row = payload["data"]["record"]

        if row["is_active"]:
            print(f"Subscribing to {row["broadcaster_user_id"]}")
            await subscribe_to_websocket(self.bot, broadcaster_user_id)
        else:
            print(f"Unsubscribing to {row["broadcaster_user_id"]}")
            await unsubscribe_from_websocket(self.bot, broadcaster_user_id)

    async def on_row_insert(self, payload):
        row = payload["data"]["record"]
        if row["is_active"]:
            print(f"Subscribing to {row["broadcaster_user_id"]}")
            await subscribe_to_websocket(self.bot, row["broadcaster_user_id"])
