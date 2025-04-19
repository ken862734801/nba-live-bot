import asyncio
import json
import aiohttp
import websockets

from commands.command import CommandHandler, record_command, score_command

BOT_USER_ID = ""
OAUTH_TOKEN = ""
CLIENT_ID = ""
CHAT_CHANNEL_USER_ID = ""
EVENTSUB_WEBSOCKET_URL = "wss://eventsub.wss.twitch.tv/ws"

# https://id.twitch.tv/oauth2/authorize
#   ?client_id=CLIENT_ID
#   &redirect_uri=http://localhost
#   &response_type=token
#   &scope=user:read:chat+user:write:chat

class Bot:
    def __init__(self):
        self.bot_user_id = BOT_USER_ID
        self.oauth_token = OAUTH_TOKEN
        self.client_id = CLIENT_ID
        self.chat_channel_user_id = CHAT_CHANNEL_USER_ID
        self.ws_url = EVENTSUB_WEBSOCKET_URL
        self.websocket_session_id: str | None = None

        self.command_handler = CommandHandler(self)
        self.command_handler.register_command("record", record_command)
        self.command_handler.register_command("score", score_command)
    
    async def validate_token(self):
        url = "https://id.twitch.tv/oauth2/validate"
        headers = {"Authorization": f"OAuth {self.oauth_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    data = await response.json()
                    print(f"Token is not valid. /oauth2/validate returned status code {response.status}")
                    raise SystemExit(1)
                print("Validated token.")
    
    async def send_chat_message(self, message: str):
        url = "https://api.twitch.tv/helix/chat/messages"
        headers = {
            "Authorization": f"Bearer {self.oauth_token}",
            "Client-Id": self.client_id,
            "Content-Type": "application/json"
        }
        body = {
            "broadcaster_id": self.chat_channel_user_id,
            "sender_id": self.bot_user_id,
            "message": message
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as response:
                if response.status != 200:
                    data = await response.json()
                    print("Failed to send chat message.")
                    print(data)
                else:
                    print(f"Sent chat message: {message}")
    
    async def register_eventsub_listeners(self):
        url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        headers = {
            "Authorization": f"Bearer {self.oauth_token}",
            "Client-Id": self.client_id,
            "Content-Type": "application/json"
        }
        body = {
            "type": "channel.chat.message",
            "version": "1",
            "condition": {
                "broadcaster_user_id": self.chat_channel_user_id,
                "user_id": self.bot_user_id
            },
            "transport": {
                "method": "websocket",
                "session_id": self.websocket_session_id
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=body) as response:
                if response.status != 202:
                    data = await response.json()
                    print(f"Subscription failed ({response.status}): {data}")
                    raise SystemExit(1)
                data = await response.json()
                subscription_id = data["data"][0]["id"]
                print(f"Subscribed to channel.chat.message [{subscription_id}]")
    
    async def handle_ws_message(self, raw: str):
        data = json.loads(raw)
        mtype = data["metadata"]["message_type"]

        if mtype == "session_welcome":
            self.websocket_session_id = data["payload"]["session"]["id"]
            print(f"Session welcome: {self.websocket_session_id}")
            await self.register_eventsub_listeners()

        elif mtype == "notification":
                event = data["payload"]["event"]
                user = event["chatter_user_login"]
                text = event["message"]["text"].strip()

                print(f"Received message: {text}")
                await self.command_handler.handle(user, text)

    async def run(self):
        await self.validate_token()
        async with websockets.connect(self.ws_url) as ws:
            async for message in ws:
                await self.handle_ws_message(message)

if __name__ == "__main__":
    bot = Bot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("Bot stopped.")