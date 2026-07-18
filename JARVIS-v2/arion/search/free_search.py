# arion/search/free_search.py

import re
import time
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


class FreeSearchEngine:
    """
    Free Search Engine - No API Keys!
    Uses DuckDuckGo (Primary), Wikipedia (Facts), and direct fetching for analysis.
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        print("✅ [Search] Free Search Engine Ready")

    def duckduckgo_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using DuckDuckGo (Requires duckduckgo-search library)"""
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('href', ''),
                        'snippet': r.get('body', ''),
                        'source': 'duckduckgo'
                    })
            return results
        except Exception as e:
            print(f"⚠️ [DDG] Error: {e}")
            return []

    def wikipedia_summary(self, query: str) -> Optional[str]:
        """Fetch Wikipedia summary without API key"""
        try:
            api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(query.replace(' ', '_'))}"
            response = self.session.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return f"Wikipedia: {data.get('extract', '')}"
        except Exception:
            pass
        return None

    def smart_search(self, query: str, deep: bool = False) -> Dict:
        """Heuristic-based search: combines DDG and Wikipedia"""
        print(f"🔍 [Search] Query: '{query}'")
        
        result = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'results': [],
            'summary': ''
        }

        # 1. Check Wikipedia for "What is" queries
        if any(w in query.lower() for w in ['what is', 'who is', 'history of']):
            wiki = self.wikipedia_summary(query)
            if wiki:
                result['summary'] += wiki + "\n\n"

        # 2. Perform Web Search
        search_results = self.duckduckgo_search(query, max_results=3 if not deep else 6)
        result['results'] = search_results

        # 3. Build text-only summary for AI prompt
        for r in search_results[:3]:
            result['summary'] += f"• {r['title']}: {r['snippet']}\n"

        return result

    def fetch_full_content(self, url: str, max_len: int = 3000) -> str:
        """Fetch and clean text from a web page for deep analysis"""
        try:
            res = self.session.get(url, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Remove ads/scripts
                for s in soup(['script', 'style', 'nav', 'footer', 'header']):
                    s.decompose()
                text = soup.get_text(separator=' ', strip=True)
                # Cleanup whitespace
                text = re.sub(r'\s+', ' ', text)
                return text[:max_len]
        except Exception:
            pass
        return ""
