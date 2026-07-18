from typing import Dict, Any, Optional
import logging
from .jikan_client import JikanClient
from .tmdb_client import TMDBClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetadataManager:
    """Unified interface for fetching metadata across different content types."""

    def __init__(self):
        self.jikan = JikanClient()
        self.tmdb = TMDBClient()

    def search_content(self, title: str, content_type: str = 'auto') -> Optional[Dict[str, Any]]:
        """
        Search for content.
        content_type can be 'anime', 'series', or 'auto' (tries anime first, then series).
        """
        logger.info(f"Searching for '{title}' (type: {content_type})...")

        if content_type in ['anime', 'auto']:
            logger.info("Attempting Jikan (Anime) search...")
            anime_results = self.jikan.search_anime(title, limit=1)
            if anime_results and anime_results.get('data'):
                anime = anime_results['data'][0]
                return {
                    'source': 'jikan',
                    'id': anime['mal_id'],
                    'title': anime.get('title'),
                    'synopsis': anime.get('synopsis'),
                    'score': anime.get('score'),
                    'episodes': anime.get('episodes'),
                    'image_url': anime.get('images', {}).get('jpg', {}).get('image_url')
                }

        if content_type in ['series', 'auto']:
            logger.info("Attempting TMDB (Series) search...")
            series_results = self.tmdb.search_tv_series(title)
            if series_results and series_results.get('results'):
                series = series_results['results'][0]
                return {
                    'source': 'tmdb',
                    'id': series['id'],
                    'title': series.get('name'),
                    'synopsis': series.get('overview'),
                    'score': series.get('vote_average'),
                    'first_air_date': series.get('first_air_date')
                }

        logger.warning(f"No results found for '{title}'.")
        return None

if __name__ == "__main__":
    manager = MetadataManager()
    
    # Test Anime
    print("\n--- Test Anime ---")
    result = manager.search_content("Death Note", content_type="anime")
    print(result)

    # Test Series
    print("\n--- Test Series ---")
    result = manager.search_content("The Boys", content_type="series")
    print(result)
