import time
import random

class KeywordHandler:
    def __init__(self):
        self.cooldowns = {}
        self.duration = 60
    
        self.handlers = {
            "lakers": self.handle_lakers_keyword
        }
    
    def _is_on_cooldown(self, channel):
        curr = time.time()
        prev = self.cooldowns.get(channel, 0)
        if curr - prev < self.duration:
            return True
        self.cooldowns[channel] = curr
        return False
    
    def get_response(self, message: str, channel:str) -> str | None:
        content = message.strip().lower()

        if content.startswith("!"):
            return None

        if self._is_on_cooldown(channel):
            return None
        
        for keyword, handler in self.handlers.items():
            if keyword in content:
                return handler()
        return None
    
    def handle_lakers_keyword(self):
        options = [
            "OKC, KFC, UFC - Lakers in 5 🖐🏾",
            "Chris Paul, Jake Paul, Logan Paul - Lakers in 5 🖐🏾",
            "Tyler Herro, Super Hero, Guitar Hero - Lakers in 5 🖐🏾"
            "Lakers in 5 🖐🏾"
        ]
        return random.choice(options)
