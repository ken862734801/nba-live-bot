class ProxyManager:
    """
    Provides a single rotating-proxy URL for all requests.
    """
    def __init__(self, proxy_url: str):
        """
        Args:
            proxy_url (str): The full HTTP(s) proxy URL, including credentials and port.
        """
        self._proxy = proxy_url

    async def get_proxy(self) -> str:
        """
        Return the rotating-proxy URL.
        """
        return self._proxy
