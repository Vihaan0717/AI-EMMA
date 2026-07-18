import asyncio
import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from search.web_brain import WebBrain
from memory.memory_manager import MemoryManager

logging.basicConfig(level=logging.INFO)

async def test_web_brain():
    print("--- Starting Web Brain Test ---")
    
    # We need a memory manager for the test
    memory = MemoryManager()
    await memory.initialize()
    
    # Initialize WebBrain
    # Note: This test assumes SearXNG might NOT be running yet, 
    # but it will test the direct sources (Wikipedia) which should work.
    web = WebBrain()
    
    print("\n1. Testing Wikipedia Factual Search...")
    result = await web.learn("Who is Alan Turing?")
    if result:
        print(f"Source: {result.get('source')}")
        print(f"Title: {result.get('title')}")
        content = result.get('content', '')
        print(f"Content length: {len(content)}")
        if len(content) > 100:
            print("SUCCESS: Wikipedia factual search works!")
    else:
        print("Wikipedia search failed (might be network issue).")

    print("\n2. Testing arXiv Academic Search...")
    result = await web.learn("transformer architecture research paper")
    if result and result.get('source') == 'arxiv':
        print(f"Papers found: {len(result.get('papers', []))}")
        if result.get('papers'):
            print(f"Top paper: {result['papers'][0]['title']}")
            print("SUCCESS: arXiv academic search works!")
    else:
        print("arXiv search failed.")

    print("\n3. Testing GitHub Code Search...")
    result = await web.learn("python library for machine learning github")
    if result and result.get('source') == 'github':
        print(f"Repos found: {len(result.get('repos', []))}")
        if result.get('repos'):
            print(f"Top repo: {result['repos'][0]['full_name']}")
            print("SUCCESS: GitHub search works!")
    else:
        print("GitHub search failed.")

    await web.close()
    await memory.stop()
    print("\n--- Web Brain Test Completed ---")

if __name__ == "__main__":
    asyncio.run(test_web_brain())
