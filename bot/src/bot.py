import socket
from dotenv import load_dotenv
from nba_api_client import get_score

class Bot:
    def __init__(self, nickname, token, channel):
        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.nickname = nickname
        self.token = token
        self.channel = channel
        self.sock = None

    def connect(self):
        print("Connecting to Twitch IRC...")
        self.sock = socket.socket()
        self.sock.connect((self.server, self.port))
        self.sock.send(f"PASS oauth:{self.token}\r\n".encode())
        self.sock.send(f"NICK {self.nickname}\r\n".encode())
        self.sock.send(f"JOIN #{self.channel}\r\n".encode())

    def listen(self):
        while True:
            response = self.sock.recv(2048).decode('utf-8')
            if response.startswith("PING"):
                self.sock.send("PONG\n".encode("utf-8"))
                print("Ping received, sent Pong.")
            else:
                print(response)
                self.handle_message(response)

    def handle_message(self, message):
        if "PRIVMSG" in message:
            # Extract the username and message content
            parts = message.split(":", 2)
            if len(parts) < 3:
                return
            user = parts[1].split("!")[0]
            command = parts[2].strip()
            
            # Check if the command starts with !score
            if command.startswith("!score"):
                # Extract the team name (if provided)
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    team_name = parts[1].strip()
                    # Call get_score with the team name
                    score = get_score(team_name)
                    self.send(f"@{user} {score}")
                else:
                    # If no team name is provided, send an error message
                    self.send(f"@{user} Please provide a team name. Usage: !score <team_name>")
    
    def send(self, message):
        self.sock.send(f"PRIVMSG #{self.channel} :{message}\n".encode('utf-8'))
        print(f"Sent message: {message}")

    def run(self):
        self.connect()
        self.send(f"PRIVMSG #{self.channel} :Hello, I am a bot! Type !score <team_name> to get the score.")
        self.listen()