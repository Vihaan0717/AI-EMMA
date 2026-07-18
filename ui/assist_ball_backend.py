import logging
import asyncio
from typing import Dict, Any, List
from config.system_config import JarvisConfig
from search.web_brain import WebBrain

logger = logging.getLogger("Nexus.AssistBall")

class AssistBallBackend:
    """
    Backend service for the Assist Ball UI.
    Fetches curated data for News, Weather, and Movies.
    """
    def __init__(self, web_brain: WebBrain = None):
        self.web = web_brain or WebBrain()
        self.api_key_news = JarvisConfig.NEWS_API_KEY
        self.api_key_weather = JarvisConfig.OPENWEATHER_API_KEY

    async def get_news(self) -> List[Dict]:
        """Fetches top tech and world news."""
        try:
            # Fallback to web search if no API key
            if not self.api_key_news:
                logger.info("No News API key, using WebBrain...")
                results = await self.web.learn("latest top world news headlines")
                # Parse results... (simplified for mock)
                return [{"title": "Global Tech Summit 2026", "source": "Web"}]
            
            # Actual API call would go here
            return [{"title": "AI Evolution reaches new peak", "source": "Reuters"}]
        except Exception as e:
            logger.error(f"News fetch failed: {e}")
            return []

    async def get_weather(self, city: str = "Hyderabad") -> Dict:
        """Fetches current weather."""
        # Simplified mock for the blueprint
        return {"city": city, "temp": "32°C", "condition": "Sunny"}

    async def get_movies(self) -> List[Dict]:
        """Fetches trending movies."""
        return [{"title": "Nexus: The Singularity", "rating": "9.5"}]

    async def get_system_status(self) -> Dict:
        """Returns health of agents and node brain."""
        return {
            "node_brain": "ONLINE",
            "agents": {
                "jarvis": "ACTIVE",
                "arion": "ACTIVE",
                "atlas": "SLEEP"
            },
            "memory_usage": "1.2GB / 16GB"
        }
