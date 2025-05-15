import asyncio
import logging
import random
import re

from asyncio import Lock

logger = logging.getLogger(__name__)


class ProxyManager:
    def __init__(self, proxies: list[str]):
        self.proxies = proxies
        self._last_subnet = None
        self._lock = asyncio.Lock()


    async def get_proxy(self) -> str | None:
        if not self.proxies:
            return None

        async with self._lock:
            for _ in range(len(self.proxies)): 
                proxy = random.choice(self.proxies).strip()

                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', proxy)
                if not match:
                    logger.warning(f"Invalid proxy format: {proxy}")
                    continue

                ip = match.group(1)
                subnet = ip.split(".")[2]

                if subnet != self._last_subnet:
                    self._last_subnet = subnet
                    logger.info(f"Using new subnet: {subnet}")
                    logger.info(f"Using proxy: {proxy}")
                    return proxy

            return random.choice(self.proxies).strip()
