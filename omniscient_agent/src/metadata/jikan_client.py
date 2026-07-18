import requests
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JikanClient:
    """Client for interacting with the Jikan API (MyAnimeList unofficial API)."""
    
    BASE_URL = "https://api.jikan.moe/v4"

    def __init__(self):
        self.session = requests.Session()

    def search_anime(self, query: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """Search for anime by title."""
        endpoint = f"{self.BASE_URL}/anime"
        params = {"q": query, "limit": limit}
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Jikan API: {e}")
            return None

    def get_anime_details(self, anime_id: int) -> Optional[Dict[str, Any]]:
        """Get full details for a specific anime by ID."""
        endpoint = f"{self.BASE_URL}/anime/{anime_id}/full"
        try:
            response = self.session.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching anime details: {e}")
            return None

if __name__ == "__main__":
    # Simple test
    client = JikanClient()
    print("Searching for 'Naruto'...")
    results = client.search_anime("Naruto", limit=1)
    if results and 'data' in results and len(results['data']) > 0:
        anime = results['data'][0]
        print(f"Found: {anime['title']} (ID: {anime['mal_id']})")
        print(f"Synopsis: {anime.get('synopsis', 'N/A')[:100]}...")
