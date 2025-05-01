import os

from config import Config
from supabase import create_client, Client

SB: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
WS_URL = Config.SUPABASE_URL.replace("https", "wss") + "/realtime/v1"

def get_supabase_client() -> Client:
    return SB

def get_supabase_websocket_url() -> str:
    return WS_URL
