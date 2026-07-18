import requests
from bs4 import BeautifulSoup
import logging
import random

logging.basicConfig(level=logging.INFO)

# We use RSS feeds of conversational subreddits because they don't block requests
# and contain rich, human day-to-day talk, humor, and feelings.
SOURCES = [
    "https://www.reddit.com/r/CasualConversation.rss",
    "https://www.reddit.com/r/Showerthoughts.rss",
    "https://www.reddit.com/r/socialskills.rss",
    "https://www.reddit.com/r/MadeMeSmile.rss"
]

def fetch_recent_conversations():
    """
    Fetches random recent conversational threads to extract human context.
    """
    source_url = random.choice(SOURCES)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) JarvisCloudWorker/1.0'
    }
    
    try:
        logging.info(f"Scraping {source_url}...")
        response = requests.get(source_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse XML (RSS)
        soup = BeautifulSoup(response.content, 'xml')
        entries = soup.find_all('entry')
        
        extracted_text = []
        for entry in entries[:5]:  # Get top 5 recent posts
            title = entry.title.text if entry.title else ""
            content = entry.content.text if entry.content else ""
            
            # Clean HTML from content
            clean_content = BeautifulSoup(content, 'html.parser').get_text(separator=' ').strip()
            
            if title or clean_content:
                extracted_text.append(f"Title: {title}\nContent: {clean_content}")
                
        full_text = "\n\n---\n\n".join(extracted_text)
        return full_text

    except Exception as e:
        logging.error(f"Error scraping {source_url}: {e}")
        return None
