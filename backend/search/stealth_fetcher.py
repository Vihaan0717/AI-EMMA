import httpx
import trafilatura
import random
import asyncio
import time
import logging
from typing import Optional, Dict
from playwright.async_api import async_playwright
from urllib.parse import urlparse

logger = logging.getLogger("StealthFetcher")

class StealthFetcher:
    def __init__(self):
        # Real browser user agents — rotate to look human
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        ]
        self.domain_last_hit = {}      # politeness: track per-domain timing
        self.min_delay = 2.0           # min seconds between hits to same domain
        self._browser = None           # lazy-initialized Playwright
        self._playwright = None
        
    def _headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        
    async def _politeness_wait(self, url: str):
        """Don't hammer the same domain — be a good citizen."""
        domain = urlparse(url).netloc
        last = self.domain_last_hit.get(domain, 0)
        elapsed = time.time() - last
        if elapsed < self.min_delay:
            wait_time = self.min_delay - elapsed + random.uniform(0, 1)
            await asyncio.sleep(wait_time)
        self.domain_last_hit[domain] = time.time()
        
    async def fetch_simple(self, url: str) -> Optional[Dict]:
        """Fast path: plain HTTP. Works on 90% of sites."""
        await self._politeness_wait(url)
        try:
            async with httpx.AsyncClient(
                headers=self._headers(),
                timeout=15,
                follow_redirects=True,
                http2=True,                    # HTTP/2 looks more browser-like
            ) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return None
                    
                # Extract clean article text
                if not response.text or len(response.text.strip()) < 100:
                    return None
                    
                extracted = trafilatura.extract(
                    response.text,
                    include_comments=False,
                    include_tables=True,
                    include_links=False,
                    deduplicate=True,
                    favor_precision=True,
                )
                if not extracted or len(extracted) < 100:
                    return None
                    
                metadata = trafilatura.extract_metadata(response.text)
                return {
                    'url': url,
                    'title': metadata.title if metadata else None,
                    'author': metadata.author if metadata else None,
                    'date': metadata.date if metadata else None,
                    'text': extracted,
                    'method': 'http',
                }
        except Exception as e:
            logger.debug(f"Simple fetch failed for {url}: {e}")
            return None
            
    async def fetch_browser(self, url: str) -> Optional[Dict]:
        """Heavy path: full browser. For JS-rendered sites."""
        await self._politeness_wait(url)
        if self._browser is None:
            await self._init_browser()
            
        try:
            context = await self._browser.new_context(
                user_agent=random.choice(self.user_agents),
                viewport={'width': 1920, 'height': 1080},
            )
        except Exception as e:
            if "closed" in str(e).lower() or "not opened" in str(e).lower():
                logger.warning("Browser closed unexpectedly. Re-initializing...")
                await self._init_browser()
                context = await self._browser.new_context(
                    user_agent=random.choice(self.user_agents),
                    viewport={'width': 1920, 'height': 1080},
                )
            else:
                raise e
        
        page = await context.new_page()
        try:
            # Stealth: hide webdriver flag
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """)
            
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(random.uniform(1, 3))  # human-like pause
            
            html = await page.content()
            if not html or len(html.strip()) < 100:
                return None
                
            extracted = trafilatura.extract(html, favor_precision=True)
            
            return {
                'url': url,
                'text': extracted,
                'method': 'browser',
            } if extracted else None
        except Exception as e:
            logger.debug(f"Browser fetch failed for {url}: {e}")
            return None
        finally:
            await page.close()
            await context.close()
            
    async def _init_browser(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
    async def fetch(self, url: str) -> Optional[Dict]:
        """Try simple first, fall back to browser."""
        result = await self.fetch_simple(url)
        if result:
            return result
        # Only spend browser resources if simple failed
        return await self.fetch_browser(url)

    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
