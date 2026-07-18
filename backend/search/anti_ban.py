import httpx
import trafilatura
import time
import logging
from typing import Optional, Dict
from urllib.parse import urlparse

logger = logging.getLogger("AntiBanLayer")

class AntiBanLayer:
    def __init__(self):
        self.failure_counts = {}           # domain -> consecutive failures
        self.cooldowns = {}                # domain -> resume_timestamp
        self.tor_available = False # self._check_tor()
        
    async def fetch_with_recovery(self, url: str, fetcher):
        domain = urlparse(url).netloc
        
        # Check cooldown
        if domain in self.cooldowns and self.cooldowns[domain] > time.time():
            logger.info(f"Domain {domain} in cooldown, skipping")
            return None
            
        # Strategy 1: Normal fetch
        result = await fetcher.fetch(url)
        if result:
            self.failure_counts[domain] = 0
            return result
            
        # Strategy 2: Increment failure
        self.failure_counts[domain] = self.failure_counts.get(domain, 0) + 1
        
        if self.failure_counts[domain] >= 3:
            # Strategy 3: Try Tor or residential proxy (if available)
            if self.tor_available:
                logger.info(f"Switching to Tor for {domain}")
                result = await self._fetch_via_tor(url)
                if result:
                    return result
                    
            # Strategy 4: Cool down for 1 hour
            self.cooldowns[domain] = time.time() + 3600
            self.failure_counts[domain] = 0
            
            # Strategy 5: Try the cached version (Wayback Machine)
            return await self._fetch_wayback(url)
            
        return None
        
    async def _fetch_via_tor(self, url: str):
        """Tor: free anonymous routing. Slower but unblockable."""
        try:
            from httpx_socks import AsyncProxyTransport
            transport = AsyncProxyTransport.from_url("socks5://127.0.0.1:9050")
            async with httpx.AsyncClient(transport=transport, timeout=30) as c:
                r = await c.get(url)
                return {
                    'url': url,
                    'text': trafilatura.extract(r.text),
                    'method': 'tor',
                }
        except Exception:
            return None
                
    async def _fetch_wayback(self, url: str):
        """Internet Archive's Wayback Machine — free historical cache."""
        wayback_url = f"https://web.archive.org/web/2024/{url}"
        async with httpx.AsyncClient(timeout=30) as c:
            try:
                r = await c.get(wayback_url, follow_redirects=True)
                return {
                    'url': url,
                    'text': trafilatura.extract(r.text),
                    'method': 'wayback',
                    'note': 'historical_snapshot',
                }
            except Exception:
                return None
                
    def _check_tor(self) -> bool:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 9050))
            sock.close()
            return result == 0
        except Exception:
            return False
