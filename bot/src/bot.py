import os
import socket
from dotenv import load_dotenv
from command import handle_command

load_dotenv()

class Bot:
    def __init__(self):
        self.server = "irc.chat.twitch.tv"
        self.port = 6667
        self.nickname = os.getenv("NAME")
        self.token = os.getenv("TOKEN")
        self.channel = os.getenv("CHANNEL")
        self.sock = None

    def connect(self):
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
                self.handle_message(response)
                print(response)

    def handle_message(self, raw):
        parts = raw.split(':', 2)
        if len(parts) < 3:
            return
        user = parts[1].split('!')[0]
        message = parts[2].strip()
        if not message.startswith('!'):
            return
        reply = handle_command(message)
        if reply:
            self.send(f"@{user} {reply}")
    
    def send(self, message):
        self.sock.send(f"PRIVMSG #{self.channel} :{message}\n".encode('utf-8'))
        print(f"Sent message: {message}")

    def run(self):
        self.connect()
        self.listen()