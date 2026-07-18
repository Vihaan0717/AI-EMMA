import yt_dlp
import logging
import os
import requests
from typing import Optional, Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsumetClient:
    """Interacts with the Consumet API to search and extract streams from anime sites."""
    
    # Public Consumet instance (can be overridden in .env if self-hosting)
    BASE_URL = os.getenv("CONSUMET_API_URL", "https://api.consumet.org")

    def __init__(self, provider: str = "gogoanime"):
        # Provider can be gogoanime, zoro, 9anime, etc.
        self.provider = provider
        self.session = requests.Session()

    def search_anime(self, query: str) -> List[Dict[str, Any]]:
        """Searches for an anime on the specified provider."""
        endpoint = f"{self.BASE_URL}/anime/{self.provider}/{query}"
        try:
            logger.info(f"Consumet: Searching for '{query}' on {self.provider}...")
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Consumet Search failed: {e}")
            return []

    def get_anime_info(self, anime_id: str) -> Optional[Dict[str, Any]]:
        """Gets full info (including episodes) for a specific anime ID."""
        endpoint = f"{self.BASE_URL}/anime/{self.provider}/info/{anime_id}"
        try:
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Consumet Info failed: {e}")
            return None

    def get_episode_stream(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Extracts the direct streaming links (.m3u8/.mp4) for a specific episode."""
        endpoint = f"{self.BASE_URL}/anime/{self.provider}/watch/{episode_id}"
        try:
            logger.info(f"Consumet: Extracting stream for episode '{episode_id}'...")
            response = self.session.get(endpoint, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Consumet Stream Extraction failed: {e}")
            return None

class VideoAcquisition:
    """Handles downloading and streaming of video content."""

    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        self.consumet = ConsumetClient()
        
    def download_video(self, url: str) -> Optional[str]:
        """
        Downloads a video from a given URL to the download directory using yt-dlp.
        """
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
            'noplaylist': True
        }

        try:
            logger.info(f"Attempting to download video from {url}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info_dict)
                logger.info(f"Successfully downloaded to: {file_path}")
                return file_path
        except Exception as e:
            logger.error(f"Failed to download video: {e}")
            return None

    def get_stream_url(self, url: str) -> Optional[str]:
        """
        Extracts the direct stream URL without downloading the file via yt-dlp.
        """
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'noplaylist': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                return info_dict.get('url')
        except Exception as e:
            logger.error(f"Failed to extract stream URL: {e}")
            return None

if __name__ == "__main__":
    # Note: Replace with a public domain or permissible video link to test
    test_url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ" # Big Buck Bunny (Open Source)
    acq = VideoAcquisition()
    print("Stream URL:", acq.get_stream_url(test_url))
