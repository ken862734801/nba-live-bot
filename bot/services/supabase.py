import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

SB: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
WS_URL = SUPABASE_URL.replace("https", "wss") + "/realtime/v1"

def _get_supabase_client() -> Client:
    return SB

def get_supabase_websocket_url() -> str:
    return WS_URL
