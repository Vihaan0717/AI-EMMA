import asyncio
from crawl4ai import AsyncWebCrawler

class HarvesterAgent:
    """
    Agent responsible for harvesting web content using Crawl4AI.
    Bypasses UI volatility and extracts clean Markdown for analysis.
    """
    def __init__(self):
        pass
        
    async def harvest_article(self, url: str) -> str:
        """
        Crawls the given URL and returns the extracted markdown content.
        """
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(url=url)
            if result.success:
                return result.markdown
            else:
                raise Exception(f"Failed to crawl {url}: {result.error_message}")

# Example Usage:
# harvester = HarvesterAgent()
# markdown_content = asyncio.run(harvester.harvest_article("https://example.com/article"))
