import os

from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class Config:
    BOT_ID = os.getenv("TWITCH_BOT_ID")
    BOT_USERNAME = os.getenv("TWITCH_BOT_USERNAME")
    CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
    DOCUMENTATION_URL = os.getenv("DOCUMENTATION_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
    TWITCH_REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")
