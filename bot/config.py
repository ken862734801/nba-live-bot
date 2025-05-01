import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_ID = os.getenv("TWITCH_BOT_ID")
    CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
    TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
    TWITCH_REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")    
    