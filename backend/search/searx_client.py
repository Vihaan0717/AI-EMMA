import httpx
import logging
from typing import Optional, List
from dataclasses import dataclass

logger = logging.getLogger("SearXNGClient")

@dataclass
class SearchResult:
    title: str
    url: str
    content: str           # Snippet
    engine: str            # Which search engine found it
    score: float           # SearXNG's relevance score

class SearXNGClient:
    def __init__(self, base_url: str = "http://localhost:8888"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=15)
        
    async def search(
        self, 
        query: str, 
        categories: List[str] = None,
        engines: List[str] = None,
        language: str = "en",
        max_results: int = 20,
    ) -> List[SearchResult]:
        """
        Categories: general, images, videos, news, science, files, it
        Engines: google, bing, duckduckgo, wikipedia, arxiv, github, ...
        """
        params = {
            'q': query,
            'format': 'json',
            'language': language,
            'safesearch': 1,
        }
        if categories:
            params['categories'] = ','.join(categories)
        if engines:
            params['engines'] = ','.join(engines)
            
        try:
            response = await self.client.get(
                f"{self.base_url}/search", 
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for r in data.get('results', [])[:max_results]:
                results.append(SearchResult(
                    title=r.get('title', ''),
                    url=r.get('url', ''),
                    content=r.get('content', ''),
                    engine=r.get('engine', 'unknown'),
                    score=r.get('score', 0.0),
                ))
            return results
        except Exception as e:
            logger.error(f"SearXNG search failed: {e}")
            logger.info("Falling back to DuckDuckGo...")
            return await self._fallback_duckduckgo(query, max_results)

    async def _fallback_duckduckgo(self, query: str, max_results: int) -> List[SearchResult]:
        try:
            from duckduckgo_search import DDGS
            import asyncio
            
            def search_sync():
                with DDGS() as ddgs:
                    return list(ddgs.text(query, max_results=max_results))
                    
            results = await asyncio.to_thread(search_sync)
            parsed_results = []
            for r in results:
                parsed_results.append(SearchResult(
                    title=r.get('title', ''),
                    url=r.get('href', ''),
                    content=r.get('body', ''),
                    engine='duckduckgo (fallback)',
                    score=0.5
                ))
            return parsed_results
        except Exception as ddg_err:
            logger.error(f"DuckDuckGo fallback also failed: {ddg_err}")
            return []
        
    async def search_science(self, query: str) -> List[SearchResult]:
        """Specifically academic sources: arxiv, semantic scholar, etc."""
        return await self.search(
            query, 
            categories=['science'],
            engines=['arxiv', 'semantic scholar', 'pubmed', 'crossref']
        )
        
    async def search_code(self, query: str) -> List[SearchResult]:
        return await self.search(
            query,
            categories=['it'],
            engines=['github', 'stackoverflow', 'gitlab']
        )
        
    async def search_news(self, query: str) -> List[SearchResult]:
        return await self.search(query, categories=['news'])
