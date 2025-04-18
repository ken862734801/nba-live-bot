import asyncio
import json

import aiohttp
import websockets

# ——— CONFIG ———
BOT_USER_ID = ''
OAUTH_TOKEN = ''       # needs scopes: user:bot, user:read:chat, user:write:chat
CLIENT_ID = ''
CHAT_CHANNEL_USER_ID = ''
EVENTSUB_WEBSOCKET_URL = 'wss://eventsub.wss.twitch.tv/ws'
# ——————————

# https://id.twitch.tv/oauth2/authorize
#   ?client_id=YOUR_CLIENT_ID
#   &redirect_uri=http://localhost
#   &response_type=token
#   &scope=user:read:chat+user:write:chat

class TwitchBot:
    def __init__(self):
        self.bot_user_id = BOT_USER_ID
        self.oauth_token = OAUTH_TOKEN
        self.client_id = CLIENT_ID
        self.chat_channel_user_id = CHAT_CHANNEL_USER_ID
        self.ws_url = EVENTSUB_WEBSOCKET_URL
        self.websocket_session_id: str | None = None

        # Command registry: map command names to handler methods
        self.commands: dict[str, callable] = {
            "hello": self.cmd_hello,
        }

    async def validate_token(self):
        url = 'https://id.twitch.tv/oauth2/validate'
        headers = {'Authorization': f'OAuth {self.oauth_token}'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    data = await resp.json()
                    print(f"Token validation failed ({resp.status}): {data}")
                    raise SystemExit(1)
                print("✅ Token validated.")

    async def send_chat_message(self, message: str):
        url = 'https://api.twitch.tv/helix/chat/messages'
        headers = {
            'Authorization': f'Bearer {self.oauth_token}',
            'Client-Id': self.client_id,
            'Content-Type': 'application/json'
        }
        payload = {
            'broadcaster_id': self.chat_channel_user_id,
            'sender_id': self.bot_user_id,
            'message': message
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    data = await resp.json()
                    print("❌ Failed to send chat message:", data)
                else:
                    print(f"✉️ Sent chat message: {message}")

    async def register_eventsub_listeners(self):
        url = 'https://api.twitch.tv/helix/eventsub/subscriptions'
        headers = {
            'Authorization': f'Bearer {self.oauth_token}',
            'Client-Id': self.client_id,
            'Content-Type': 'application/json'
        }
        payload = {
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
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 202:
                    data = await resp.json()
                    print(f"❌ Subscription failed ({resp.status}): {data}")
                    raise SystemExit(1)
                data = await resp.json()
                sub_id = data['data'][0]['id']
                print(f"✅ Subscribed to channel.chat.message [{sub_id}]")

    async def handle_ws_message(self, raw: str):
        data = json.loads(raw)
        mtype = data['metadata']['message_type']

        if mtype == 'session_welcome':
            # save session ID and subscribe
            self.websocket_session_id = data['payload']['session']['id']
            print("🔑 Received session_welcome, session_id =", self.websocket_session_id)
            await self.register_eventsub_listeners()

        elif mtype == 'notification':
            stype = data['metadata']['subscription_type']
            if stype == 'channel.chat.message':
                ev = data['payload']['event']
                user = ev['chatter_user_login']
                text = ev['message']['text'].strip()
                channel = ev['broadcaster_user_login']
                print(f"MSG #{channel} <{user}> {text}")

                # Command handling
                if text.startswith('!'):
                    parts = text[1:].split()
                    cmd_name = parts[0].lower()
                    args = parts[1:]
                    handler = self.commands.get(cmd_name)
                    if handler:
                        await handler(user, args)
                    else:
                        print(f"Unknown command: {cmd_name}")
                # Fallback hardcoded response
                elif text == "HeyGuys":
                    await self.send_chat_message("VoHiYo")

    # Command implementation
    async def cmd_hello(self, user: str, args: list[str]):
        """!hello → Hello, World! (mentions the caller)"""
        # mention the user who invoked the command
        await self.send_chat_message(f"@{user} Hello, World LUL")

    async def run(self):
        # 1) validate token
        await self.validate_token()

        # 2) open websocket and listen
        async with websockets.connect(self.ws_url) as ws:
            print(f"🔗 WebSocket connected to {self.ws_url}")
            async for message in ws:
                await self.handle_ws_message(message)


if __name__ == '__main__':
    bot = TwitchBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
