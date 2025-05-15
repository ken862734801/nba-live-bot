from twitchio import eventsub


class WebSocketManager:
    def __init__(self, bot):
        self.bot = bot

    async def subscribe(self, broadcaster_user_id: str) -> None:
        subscription = eventsub.ChatMessageSubscription(
            broadcaster_user_id=broadcaster_user_id,
            user_id=self.bot.bot_id,
        )
        await self.bot.subscribe_websocket(payload=subscription)

    async def unsubscribe(self, broadcaster_user_id: str) -> None:
        subscription = self.bot.websocket_subscriptions()
        for subscription_id, data in subscription.items():
            if data.condition.get("broadcaster_user_id") == broadcaster_user_id:
                await self.bot.delete_websocket_subscription(subscription_id)
