from dotenv import load_dotenv

class Bot:
    def __init__(self):
        self.server = "irc.chat.twitch.tv"

    def connect(self):
        print("Connecting to Twitch IRC...")

    def run(self):
        self.connect()

    