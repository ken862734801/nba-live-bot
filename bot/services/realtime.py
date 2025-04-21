import os
import asyncio
from realtime import AsyncRealtimeClient
from services.supabase import get_supabase_websocket_url
from services.eventsub import subscribe_to_twitch_chat, unsubscribe_from_twitch_chat

class RealtimeListener:
    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncRealtimeClient(get_supabase_websocket_url(), os.getenv("SUPABASE_KEY"), auto_reconnect=True)
    
    async def start(self):
        await self.client.connect()
        channel = self.client.channel("realtime:public:channels")

        channel.on_postgres_changes(event="UPDATE", schema="public", table="channels", callback=lambda payload: asyncio.create_task(self.on_row_update(payload)))
        channel.on_postgres_changes(event="INSERT", schema="public", table="channels", callback=lambda payload: asyncio.create_task(self.on_row_insert(payload)))

        await channel.subscribe()
        asyncio.create_task(self._start_heartbeat_loop())
    
    async def _start_heartbeat_loop(self):
        while True:
            await asyncio.sleep(1)

    async def on_row_update(self, payload):
        row = payload["data"]["record"]

        if row["is_active"]:
            print(f"Subscribing to {row["broadcaster_user_id"]}")
            await subscribe_to_twitch_chat(self.bot, broadcaster_user_id)
        else:
            print(f"Unsubscribing to {row["broadcaster_user_id"]}")
            await unsubscribe_from_twitch_chat(self.bot, broadcaster_user_id)

    async def on_row_insert(self, payload):
        row = payload["data"]["record"]
        if row["is_active"]:
            print(f"Subscribing to {row["broadcaster_user_id"]}")
            await subscribe_to_twitch_chat(self.bot, row["broadcaster_user_id"])
