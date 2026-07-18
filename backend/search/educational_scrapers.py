import logging
import re
import httpx
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs
from .stealth_fetcher import StealthFetcher

logger = logging.getLogger("EducationalScrapers")

class YouTubeScraper:
    """Scrapes YouTube search results and fetches transcripts or description/metadata."""
    
    def __init__(self):
        self.fetcher = StealthFetcher()
        
    async def search_and_extract(self, query: str, searx_client) -> List[Dict]:
        """Searches YouTube and extracts transcripts or descriptions."""
        # 1. Search YouTube videos via SearXNG or fallback
        search_query = f"{query} youtube"
        results = await searx_client.search(search_query, max_results=5)
        
        extracted = []
        for r in results:
            url = r.url
            video_id = self._extract_video_id(url)
            if not video_id:
                continue
                
            # Attempt to fetch transcript
            transcript = await self._get_transcript(video_id)
            
            extracted.append({
                'title': r.title,
                'url': url,
                'video_id': video_id,
                'description': r.content,
                'transcript': transcript or "No transcript available. Falling back to video metadata and summary.",
                'source': 'youtube'
            })
            
        return extracted
        
    def _extract_video_id(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        if not parsed.hostname:
            return None
            
        hostname = parsed.hostname.lower()
        if hostname in ('youtu.be', 'www.youtu.be'):
            return parsed.path[1:]
            
        if 'youtube.com' in hostname:
            if parsed.path == '/watch':
                p = parse_qs(parsed.query)
                return p.get('v', [None])[0]
            if parsed.path.startswith('/embed/'):
                return parsed.path.split('/')[2]
            if parsed.path.startswith('/v/'):
                return parsed.path.split('/')[2]
            if parsed.path.startswith('/shorts/'):
                return parsed.path.split('/')[2]
        return None

    async def _get_transcript(self, video_id: str) -> Optional[str]:
        """Attempts to use youtube-transcript-api if installed, else fallback."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            formatter_imported = False
            try:
                from youtube_transcript_api.formatters import TextFormatter
                formatter_imported = True
            except ImportError:
                pass
                
            # Get transcripts (English preferred)
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'te', 'hi'])
            if formatter_imported:
                formatter = TextFormatter()
                return formatter.format_transcript(transcript_list)
            else:
                return " ".join([t['text'] for t in transcript_list])
        except Exception as e:
            logger.debug(f"Failed to fetch transcript for video {video_id}: {e}")
            return None

class EducationalScraper:
    """Scrapes authoritative open learning and academic databases."""
    
    def __init__(self):
        self.fetcher = StealthFetcher()
        self.edu_domains = [
            "khanacademy.org",
            "britannica.com",
            "nature.com",
            "sciencedirect.com",
            "plato.stanford.edu",
            "mit.edu",
            "harvard.edu",
            "stanford.edu"
        ]
        
    async def search_and_scrape(self, query: str, searx_client) -> List[Dict]:
        """Searches academic/educational domains and returns detailed articles."""
        # Restrict search to edu domains
        domain_filter = " OR ".join([f"site:{d}" for d in self.edu_domains])
        search_query = f"({query}) ({domain_filter})"
        
        results = await searx_client.search(search_query, max_results=5)
        scraped_docs = []
        
        for r in results:
            try:
                # Scrape full text from the page
                page_text = await self.fetcher.fetch(r.url)
                if page_text:
                    # Clean up basic tags or long spaces
                    clean_text = re.sub(r'\s+', ' ', page_text).strip()
                    # Cap size to avoid flooding LLM context
                    scraped_docs.append({
                        'title': r.title,
                        'url': r.url,
                        'content': clean_text[:8000], # Top 8k chars
                        'source': urlparse(r.url).netloc
                    })
            except Exception as e:
                logger.debug(f"Failed to scrape educational site {r.url}: {e}")
                
        return scraped_docs
