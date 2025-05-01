import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_ID = os.getenv("TWITCH_BOT_ID")
    CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
    SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndveW9odWV3ZmtiemFyeGFhenRxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDUwNzUwMzMsImV4cCI6MjA2MDY1MTAzM30.iclPSTZDqFw8BLhzYTiFervTrovk0USFtzt6ff5Oo8M"
    SUPABASE_URL="https://woyohuewfkbzarxaaztq.supabase.co"
    TWITCH_ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
    TWITCH_REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")    
    