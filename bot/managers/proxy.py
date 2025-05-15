import asyncio
import logging
import random
import re

from asyncio import Lock

logger = logging.getLogger(__name__)


class ProxyManager:
    """
    Manages a pool of proxy endpoints and provides a method to retrieve
    a proxy whose IP subnet differs from the last one used, to help distribute
    requests across different network segments.
    """

    def __init__(self, proxies: list[str]):
        """
        Initialize the ProxyManager.

        Args:
            proxies (list[str]): A list of proxy URLs or address strings.
        """
        self.proxies = proxies
        self._last_subnet = None
        self._lock = asyncio.Lock()

    async def get_proxy(self) -> str | None:
        """
        Asynchronously select and return a proxy whose IP subnet differs from
        the last subnet used. If no new-subnet proxy is found after one full
        pass, returns a random proxy from the list. If the proxy list is empty,
        returns None.

        Returns:
            str | None: A proxy string, or None if no proxies are configured.
        """
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

            fallback = random.choice(self.proxies).strip()
            logger.info(f"No new-subnet proxy available, falling back to: {fallback}")
            return fallback
