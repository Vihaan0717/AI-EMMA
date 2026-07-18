import feedparser
import logging
import asyncio
from typing import List, Dict

logger = logging.getLogger("RSSAggregator")

class RSSAggregator:
    """Subscribe to RSS = automatic, free, unlimited learning."""
    
    def __init__(self):
        self.feeds = {
            'tech': [
                'https://hnrss.org/frontpage',           # Hacker News
                'https://www.theverge.com/rss/index.xml',
                'https://feeds.arstechnica.com/arstechnica/index',
            ],
            'science': [
                'https://rss.arxiv.org/rss/cs.AI',       # AI papers
                'https://rss.arxiv.org/rss/cs.LG',       # ML papers
                'https://www.nature.com/nature.rss',
            ],
            'security': [
                'https://krebsonsecurity.com/feed/',
                'https://www.schneier.com/feed/',
            ],
        }
        
    async def pull_all(self) -> List[Dict]:
        results = []
        for category, urls in self.feeds.items():
            for url in urls:
                try:
                    # feedparser.parse is blocking, but fast enough for RSS
                    feed = await asyncio.to_thread(feedparser.parse, url)
                    for entry in feed.entries[:20]:
                        results.append({
                            'category': category,
                            'title': entry.title,
                            'url': entry.link,
                            'summary': entry.get('summary', ''),
                            'published': entry.get('published', ''),
                        })
                except Exception as e:
                    logger.warning(f"RSS fetch failed: {url} - {e}")
        return results
