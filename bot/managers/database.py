import logging
import asyncio

from config import Config
from realtime import AsyncRealtimeClient
from supabase import Client

from managers.websocket import WebSocketManager

logger = logging.getLogger(__name__)


class DatabaseManager:
    WS_URL = Config.SUPABASE_URL.replace("https", "wss") + "/realtime/v1"

    def __init__(self, supabase_client: Client, websocket_manager: WebSocketManager):
        self.async_realtime_client = AsyncRealtimeClient(
            self.WS_URL, Config.SUPABASE_KEY, auto_reconnect=True)
        self.supabase_client = supabase_client
        self.websocket_manager = websocket_manager

    async def seed(self) -> None:
        response = self.supabase_client.table(
            "channels").select("broadcaster_user_id").eq("is_active", True).execute()
        rows = response.data
        for row in rows:
            broadcaster_user_id = row.get("broadcaster_user_id")
            if not broadcaster_user_id:
                logger.warning("Row missing 'broadcaster_user_id': %r", row)
                continue
            try:
                await self.websocket_manager.subscribe(broadcaster_user_id)
            except Exception as e:
                logger.error("Error subscribing to %s: %s",
                             broadcaster_user_id, e)

    async def listen(self):
        await self.async_realtime_client.connect()
        channel = self.async_realtime_client.channel(
            "realtime:public:channels")

        channel.on_postgres_changes(
            event="INSERT",
            schema="public",
            table="channels",
            callback=lambda payload: asyncio.create_task(
                self.on_change(payload))
        )

        channel.on_postgres_changes(
            event="UPDATE",
            schema="public",
            table="channels",
            callback=lambda payload: asyncio.create_task(
                self.on_change(payload))
        )

        await channel.subscribe()

    async def close(self):
        await self.async_realtime_client.close()

    async def on_change(self, payload):
        row = payload["data"]["record"]
        if row["is_active"]:
            await self.websocket_manager.subscribe(row["broadcaster_user_id"])
        else:
            await self.websocket_manager.unsubscribe(row["broadcaster_user_id"])
