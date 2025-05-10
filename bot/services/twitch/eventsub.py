from twitchio import eventsub


async def subscribe_to_websocket(bot, broadcaster_user_id):
    subscription = eventsub.ChatMessageSubscription(
        broadcaster_user_id=broadcaster_user_id, user_id=bot.bot_id)
    await bot.subscribe_websocket(payload=subscription)


async def unsubscribe_from_websocket(bot, broadcaster_user_id):
    subscription = bot.websocket_subscriptions()
    for subscription_id, data in subscription.items():
        if data.condition.get("broadcaster_user_id") == broadcaster_user_id:
            await bot.delete_websocket_subscription(subscription_id)
