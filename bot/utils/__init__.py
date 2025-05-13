import threading

from config import Config


class ProxyManager:
    def __init__(self):
        self.raw_list = Config.PROXY_LIST or ""
        self.proxy_list = [p.strip()
                           for p in self.raw_list.split(",") if p.strip()]
        self.username = Config.WEBSHARE_USERNAME
        self.password = Config.WEBSHARE_PASSWORD
        self.index = 0
        self._lock = threading.Lock()

    def get_proxy(self):
        if not (self.proxy_list and self.username and self.password):
            return None

        with self._lock:
            current_proxy = self.proxy_list[self.index]
            self.index = (self.index + 1) % len(self.proxy_list)
        url = f"http://{self.username}:{self.password}@{current_proxy}"
        return url


proxy_manager = ProxyManager()
