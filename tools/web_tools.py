import webbrowser
import urllib.parse
from core.logger import get_logger

logger = get_logger("WebTools")

class WebTools:
    """
    Tools for web interaction and search.
    """
    @staticmethod
    def open_website(url: str) -> str:
        webbrowser.open(url)
        return f"Opening {url}."

    @staticmethod
    def search_google(query: str) -> str:
        safe_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={safe_query}"
        webbrowser.open(url)
        return f"Searching Google for: {query}"

    @staticmethod
    def play_youtube(query: str) -> str:
        safe_query = urllib.parse.quote(query)
        url = f"https://www.youtube.com/results?search_query={safe_query}"
        webbrowser.open(url)
        return f"Opening YouTube results for: {query}"

    @staticmethod
    def scrape_web_context(query: str) -> str:
        """Lightweight background scraping for Free Search context."""
        import requests
        from bs4 import BeautifulSoup
        
        logger.info(f"Performing background scrape for: '{query}'")
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(search_url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract snippets from Google search result page (simplified)
            snippets = []
            for g in soup.find_all('div', limit=5):
                text = g.get_text()
                if len(text) > 50:
                    snippets.append(text[:200])
            
            context = "\n".join(snippets)
            return f"Web Context for '{query}':\n{context}" if context else "No clear web context found."
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return f"Failed to fetch ground truth for '{query}'."
