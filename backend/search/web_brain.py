import re
import asyncio
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse

from config.system_config import JarvisConfig
from .searx_client import SearXNGClient
from .stealth_fetcher import StealthFetcher
from .source_clients import WikipediaClient, ArxivClient, GitHubScraper, StackOverflowClient
from .rss_aggregator import RSSAggregator
from .anti_ban import AntiBanLayer
from .educational_scrapers import YouTubeScraper, EducationalScraper

logger = logging.getLogger("WebBrain")

class WebBrain:
    """The unified, free, no-API-key web access layer for Zero."""
    
    def __init__(self, searx_url: str = None):
        url = searx_url or JarvisConfig.SEARXNG_URL
        self.searx = SearXNGClient(url)
        self.fetcher = StealthFetcher()
        self.wikipedia = WikipediaClient()
        self.arxiv = ArxivClient()
        self.github = GitHubScraper()
        self.stackoverflow = StackOverflowClient()
        self.rss = RSSAggregator()
        self.anti_ban = AntiBanLayer()
        self.youtube = YouTubeScraper()
        self.educational = EducationalScraper()
        
        # Routing: query type → best source
        self.routing_rules = [
            (r'\b(youtube|video|watch|listen|song|music|melody)\b', self._handle_youtube),
            (r'\b(biology|chemistry|physics|science|khan|mit|harvard|stanford|article)\b', self._handle_educational),
            (r'\b(paper|research|study|arxiv)\b', self._handle_academic),
            (r'\b(code|github|library|how to)\b', self._handle_code),
            (r'\b(error|exception|bug|stacktrace)\b', self._handle_debug),
            (r'\b(what is|who is|definition|history)\b', self._handle_factual),
            (r'\b(news|today|latest|recent)\b', self._handle_news),
        ]
        
    async def _handle_youtube(self, query: str):
        videos = await self.youtube.search_and_extract(query, self.searx)
        return {
            'source': 'youtube',
            'videos': videos,
            'trust': 0.85
        } if videos else None

    async def _handle_educational(self, query: str):
        articles = await self.educational.search_and_scrape(query, self.searx)
        return {
            'source': 'educational_sites',
            'articles': articles,
            'trust': 0.90
        } if articles else None

    async def learn(self, query: str) -> Dict:
        """The single entry point Zero calls when it wants to learn."""
        logger.info(f"Learning about: {query}")
        
        # 1. Route to specialist scraper based on query intent
        for pattern, handler in self.routing_rules:
            if re.search(pattern, query, re.IGNORECASE):
                specialist_result = await handler(query)
                if specialist_result:
                    return specialist_result
                    
        # 2. Fall back to general SearXNG meta-search
        return await self._handle_general(query)
        
    async def _handle_factual(self, query: str):
        # Wikipedia first — most reliable for "what is X"
        try:
            # Clean query for Wikipedia (strip "Who is", "What is", etc.)
            clean_query = re.sub(r'^(who|what|where|when|why) is\s+', '', query, flags=re.IGNORECASE)
            clean_query = clean_query.strip(' ?')
            
            wiki_results = await self.wikipedia.search(clean_query, limit=3)
            if wiki_results and len(wiki_results) > 1 and wiki_results[1]:
                title = wiki_results[1][0]
                article = await self.wikipedia.get_full_article(title)
                return {
                    'source': 'wikipedia',
                    'title': title,
                    'content': article,
                    'trust': 0.95,
                }
        except Exception as e:
            logger.debug(f"Wikipedia factual search failed: {e}")
        return None
        
    async def _handle_academic(self, query: str):
        papers = await self.arxiv.search(query, max_results=5)
        return {
            'source': 'arxiv',
            'papers': papers,
            'trust': 0.95,
        } if papers else None
        
    async def _handle_code(self, query: str):
        repos = await self.github.search_repos(query)
        return {
            'source': 'github',
            'repos': repos[:5],
            'trust': 0.85,
        } if repos else None
        
    async def _handle_debug(self, query: str):
        answers = await self.stackoverflow.search(query)
        return {
            'source': 'stackoverflow',
            'answers': answers[:3],
            'trust': 0.80,
        } if answers else None
        
    async def _handle_news(self, query: str):
        results = await self.searx.search_news(query)
        return await self._enrich_with_full_text(results[:5])
        
    async def _handle_general(self, query: str):
        # SearXNG aggregates everything
        results = await self.searx.search(query, max_results=10)
        # Diversity filter — one result per domain
        seen_domains = set()
        diverse = []
        for r in results:
            domain = urlparse(r.url).netloc
            if domain not in seen_domains:
                diverse.append(r)
                seen_domains.add(domain)
            if len(diverse) >= 5:
                break
        # Fetch full text from top results
        return await self._enrich_with_full_text(diverse)
        
    async def _enrich_with_full_text(self, results):
        """Fetch the actual page content for top results, in parallel."""
        # Use gather for concurrency but wrapped in anti-ban recovery
        fetched = await asyncio.gather(*[
            self.anti_ban.fetch_with_recovery(r.url, self.fetcher) for r in results
        ])
        return {
            'source': 'web',
            'documents': [f for f in fetched if f is not None],
            'trust': 0.6,  # general web — needs verification
        }

    async def close(self):
        await self.fetcher.close()
        await self.searx.client.aclose()
