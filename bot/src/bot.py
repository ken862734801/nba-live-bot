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
        print("Listening for messages...")
        while True:
            response = self.sock.recv(2048).decode('utf-8')
            if response.startswith("PING"):
                self.sock.send("PONG\n".encode("utf-8"))
                print("Ping received, sent Pong.")
            else:
                print(response)
    
    def send(self, message):
        self.sock.send(f"PRIVMSG #{self.channel} :{message}\n".encode('utf-8'))
        print(f"Sent message: {message}")

    def run(self):
        self.connect()
        self.listen()