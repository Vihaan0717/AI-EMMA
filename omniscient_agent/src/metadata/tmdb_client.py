import requests
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TMDBClient:
    """Client for interacting with The Movie Database (TMDB) API."""
    
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        if not self.api_key:
            logger.warning("TMDB_API_KEY not found in environment variables. TMDB requests will fail.")
        self.session = requests.Session()

    def search_tv_series(self, query: str) -> Optional[Dict[str, Any]]:
        """Search for a TV/Web series by title."""
        if not self.api_key:
            return None
            
        endpoint = f"{self.BASE_URL}/search/tv"
        params = {
            "api_key": self.api_key,
            "query": query,
            "include_adult": "false",
            "language": "en-US"
        }
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from TMDB API: {e}")
            return None

    def get_series_details(self, series_id: int) -> Optional[Dict[str, Any]]:
        """Get full details for a specific series by TMDB ID."""
        if not self.api_key:
            return None
            
        endpoint = f"{self.BASE_URL}/tv/{series_id}"
        params = {"api_key": self.api_key, "language": "en-US"}
        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching series details: {e}")
            return None

if __name__ == "__main__":
    # Simple test (requires TMDB_API_KEY in .env)
    client = TMDBClient()
    if client.api_key:
        print("Searching for 'Breaking Bad'...")
        results = client.search_tv_series("Breaking Bad")
        if results and 'results' in results and len(results['results']) > 0:
            series = results['results'][0]
            print(f"Found: {series['name']} (ID: {series['id']})")
            print(f"Overview: {series.get('overview', 'N/A')[:100]}...")
    else:
        print("Please set TMDB_API_KEY in .env to run this test.")
