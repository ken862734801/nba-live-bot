import logging

from twitchio import eventsub

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Handles Twitch EventSub websocket subscriptions for chat messages.
    Provides methods to subscribe and unsubscribe to chat events for a given broadcaster.
    """

    def __init__(self, bot):
        """
        Initialize the WebSocketManager.

        Args:
            bot: The TwitchIO Bot instance which exposes methods to manage websocket subscriptions.
        """
        self.bot = bot

    async def subscribe(self, broadcaster_user_id: str) -> None:
        """
        Subscribe to chat message events for a specific broadcaster.

        Creates a ChatMessageSubscription for the given broadcaster_user_id and
        registers it with the bot's websocket connection.

        Args:
            broadcaster_user_id (str): The Twitch user ID of the channel to subscribe to.
        """
        subscription = eventsub.ChatMessageSubscription(
            broadcaster_user_id=broadcaster_user_id,
            user_id=self.bot.bot_id,
        )
        await self.bot.subscribe_websocket(payload=subscription)
        logger.info("Successfully joined channel: %s", broadcaster_user_id)

    async def unsubscribe(self, broadcaster_user_id: str) -> None:
        """
        Unsubscribe from chat message events for a specific broadcaster.

        Iterates through the bot's active websocket subscriptions, finds the one
        matching the given broadcaster_user_id, and deletes it.

        Args:
            broadcaster_user_id (str): The Twitch user ID of the channel to unsubscribe from.
        """
        subscriptions = self.bot.websocket_subscriptions()
        for subscription_id, data in subscriptions.items():
            if data.condition.get("broadcaster_user_id") == broadcaster_user_id:
                await self.bot.delete_websocket_subscription(subscription_id)
