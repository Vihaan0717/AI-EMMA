import httpx
import logging
from typing import List, Dict, Optional

logger = logging.getLogger("SourceClients")

class WikipediaClient:
    """Wikipedia explicitly allows scraping. Use their REST API (no key needed)."""
    BASE = "https://en.wikipedia.org/api/rest_v1"
    HEADERS = {'User-Agent': 'JARVIS-Project/1.0 (vanger.vihaan@gmail.com)'}
    
    async def search(self, query: str, limit: int = 10):
        async with httpx.AsyncClient(headers=self.HEADERS) as c:
            r = await c.get(
                f"https://en.wikipedia.org/w/api.php",
                params={
                    'action': 'opensearch',
                    'search': query,
                    'limit': limit,
                    'format': 'json',
                }
            )
            return r.json()
            
    async def get_summary(self, title: str):
        async with httpx.AsyncClient(headers=self.HEADERS) as c:
            r = await c.get(f"{self.BASE}/page/summary/{title}")
            return r.json() if r.status_code == 200 else None
            
    async def get_full_article(self, title: str):
        """Full clean article text."""
        async with httpx.AsyncClient(headers=self.HEADERS) as c:
            r = await c.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    'action': 'query',
                    'prop': 'extracts',
                    'explaintext': 1,
                    'titles': title,
                    'format': 'json',
                }
            )
            data = r.json()
            pages = data['query']['pages']
            return next(iter(pages.values())).get('extract', '')

class ArxivClient:
    HEADERS = {'User-Agent': 'JARVIS-Project/1.0 (vanger.vihaan@gmail.com)'}
    async def search(self, query: str, max_results: int = 10):
        async with httpx.AsyncClient(follow_redirects=True, headers=self.HEADERS) as c:
            r = await c.get(
                "https://export.arxiv.org/api/query",
                params={
                    'search_query': f'all:{query}',
                    'max_results': max_results,
                    'sortBy': 'relevance',
                }
            )
            # Parse Atom XML (arxiv returns XML, not JSON)
            import feedparser
            feed = feedparser.parse(r.text)
            return [{
                'title': e.title,
                'authors': [a.name for a in e.authors],
                'summary': e.summary,
                'pdf_url': next(l.href for l in e.links if l.type == 'application/pdf'),
                'published': e.published,
            } for e in feed.entries]

class GitHubScraper:
    """Public GitHub data — no token needed for read-only at low rates."""
    async def search_repos(self, query: str):
        async with httpx.AsyncClient() as c:
            r = await c.get(
                "https://api.github.com/search/repositories",
                params={'q': query, 'sort': 'stars', 'order': 'desc'},
                headers={'Accept': 'application/vnd.github.v3+json'},
            )
            return r.json()['items'] if r.status_code == 200 else []
            
    async def get_readme(self, owner: str, repo: str):
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
        async with httpx.AsyncClient() as c:
            r = await c.get(url)
            if r.status_code == 404:
                r = await c.get(url.replace('/main/', '/master/'))
            return r.text if r.status_code == 200 else None

class StackOverflowClient:
    BASE = "https://api.stackexchange.com/2.3"
    HEADERS = {'User-Agent': 'JARVIS-Project/1.0 (vanger.vihaan@gmail.com)'}
    
    async def search(self, query: str):
        async with httpx.AsyncClient(follow_redirects=True, headers=self.HEADERS) as c:
            r = await c.get(
                f"{self.BASE}/search/advanced",
                params={
                    'q': query,
                    'site': 'stackoverflow',
                    'sort': 'votes',
                    'order': 'desc',
                    'filter': 'withbody',  # include answer bodies
                }
            )
            return r.json().get('items', [])
