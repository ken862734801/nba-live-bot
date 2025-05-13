from nba_api.live.nba.endpoints import scoreboard

from config import Config

def with_proxy(proxy: str):
    try:
        scoreboard.ScoreBoard(proxy=proxy)
        print(f"THE PROXY WORKS!") 
    except Exception as e:
        print(f"THE PROXY DOES NOT WORK! {e}")

if __name__ == "__main__":
    with_proxy(Config.PROXY)