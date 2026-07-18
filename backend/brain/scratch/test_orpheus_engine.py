import asyncio
import sys
import os
import time
from pathlib import Path

# Add project root to sys.path
root = Path(r'c:\Users\anger\Desktop\JARVIS_Project')
sys.path.append(str(root))

from services.music_service import music_service

def safe_print(text):
    print("".join(c if ord(c) < 128 else '?' for c in str(text)))

async def test_music_engine():
    safe_print("--- Testing Orpheus Music Engine ---")
    
    # 1. Search and Add
    query = "lofi hip hop"
    safe_print(f"Action: Searching for '{query}'...")
    result = music_service.search_and_add(query)
    safe_print(f"Result: {result}")
    
    # Wait for stream to start
    safe_print("Waiting 10s for playback to stabilize...")
    time.sleep(10)
    
    # 2. Check Status
    status = music_service.get_status()
    safe_print(f"Current Status: {status}")
    
    # Check if we have a title in queue
    if status['current_song'] != "None":
        safe_print("SUCCESS: Song found and added.")
    else:
        safe_print("FAILURE: No song found.")
        return

    # 3. Test Controls
    safe_print("Action: Pausing...")
    safe_print(music_service.pause())
    time.sleep(2)
    
    safe_print("Action: Resuming...")
    safe_print(music_service.resume())
    time.sleep(2)
    
    safe_print("Action: Seeking +30s...")
    safe_print(music_service.seek(30))
    time.sleep(2)

    # 4. Cleanup
    safe_print("Action: Stopping...")
    music_service.stop()
    safe_print("Test complete.")

if __name__ == "__main__":
    asyncio.run(test_music_engine())
