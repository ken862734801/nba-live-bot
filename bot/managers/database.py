import logging
import asyncio

from config import Config
from realtime import AsyncRealtimeClient
from supabase import Client

from managers.websocket import WebSocketManager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages channel subscriptions by syncing the Supabase `channels` table
    with the WebSocketManager. It performs an initial subscribe to all
    active channels and then listens for real-time INSERT/UPDATE events
    to subscribe or unsubscribe dynamically.
    """
    WS_URL = Config.SUPABASE_URL.replace("https", "wss") + "/realtime/v1"

    def __init__(self, supabase_client: Client, websocket_manager: WebSocketManager):
        """
        Initialize your DatabaseManager.

        Args:
            supabase_client (Client): A Supabase client for querying the `channels` table.
            websocket_manager (WebSocketManager): Handles actual subscribe/unsubscribe calls
                                                   to Twitch over WebSockets.
        """
        self.async_realtime_client = AsyncRealtimeClient(
            self.WS_URL, Config.SUPABASE_KEY, auto_reconnect=True
        )
        self.supabase_client = supabase_client
        self.websocket_manager = websocket_manager

    async def init(self) -> None:
        """
        Perform the initial subscription to all currently active channels.

        Queries Supabase for rows in `channels` where `is_active` is True,
        then calls WebSocketManager.subscribe on each valid broadcaster_user_id.
        Logs and skips any rows missing the broadcaster_user_id.
        """
        response = (
            self.supabase_client
            .table("channels")
            .select("broadcaster_user_id")
            .eq("is_active", True)
            .execute()
        )
        rows = response.data
        print(rows)
        for row in rows:
            broadcaster_user_id = row.get("broadcaster_user_id")
            if not broadcaster_user_id:
                logger.warning("Row missing 'broadcaster_user_id': %r", row)
                continue
            try:
                await self.websocket_manager.subscribe(broadcaster_user_id)
            except Exception as e:
                logger.error("Error subscribing to %s: %s", broadcaster_user_id, e)

    async def listen(self) -> None:
        """
        Connect to Supabase Realtime and subscribe to INSERT and UPDATE
        events on the `channels` table.

        For each relevant change, schedules self.on_change to handle the payload.
        """
        await self.async_realtime_client.connect()
        channel = self.async_realtime_client.channel("realtime:public:channels")

        # Listen for new channels being added
        channel.on_postgres_changes(
            event="INSERT",
            schema="public",
            table="channels",
            callback=lambda payload: asyncio.create_task(self.on_change(payload)),
        )

        # Listen for changes to existing channels
        channel.on_postgres_changes(
            event="UPDATE",
            schema="public",
            table="channels",
            callback=lambda payload: asyncio.create_task(self.on_change(payload)),
        )

        await channel.subscribe()

    async def close(self) -> None:
        """
        Close the Supabase Realtime connection cleanly.
        """
        await self.async_realtime_client.close()

    async def on_change(self, payload: dict) -> None:
        """
        Handle a real-time change event from Supabase.

        Args:
            payload (dict): The change payload, containing 'data' -> 'record'.

        Behavior:
            - If record['is_active'] is True, subscribe to that channel.
            - Otherwise, unsubscribe from that channel.
        """
        row = payload["data"]["record"]
        broadcaster_user_id = row.get("broadcaster_user_id")
        if not broadcaster_user_id:
            logger.warning("Change payload missing 'broadcaster_user_id': %r", row)
            return

        if row["is_active"]:
            await self.websocket_manager.subscribe(broadcaster_user_id)
        else:
            await self.websocket_manager.unsubscribe(broadcaster_user_id)
