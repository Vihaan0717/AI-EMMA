import os
import time
import logging
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.fleet.local_db import fleet_db
from brain.ingestion.ingest_obsidian import ObsidianIngestionAgent
from pathlib import Path
import asyncio

logger = logging.getLogger("ObsidianWatcher")

class ObsidianKnowledgeHandler(FileSystemEventHandler):
    """
    Monitors Obsidian Markdown files.
    When a file is created or modified, it increments ENT (Entity) points for the fleet.
    """
    def __init__(self, vault_path, loop=None):
        self.vault_path = Path(vault_path)
        self.db_path = "memory/fleet.db"
        self.agent = ObsidianIngestionAgent(self.vault_path)
        self.loop = loop or asyncio.get_event_loop()

    def on_modified(self, event):
        if event.src_path.endswith(".md"):
            filename = os.path.basename(event.src_path)
            logger.info(f"Knowledge Update: {filename}")
            self._increment_ent_points()
            # Neural Sync
            asyncio.run_coroutine_threadsafe(self.agent.sync_file(Path(event.src_path)), self.loop)

    def on_created(self, event):
        if event.src_path.endswith(".md"):
            filename = os.path.basename(event.src_path)
            logger.info(f"New Entity Detected: {filename}")
            self._increment_ent_points(gain=5)
            # Neural Sync
            asyncio.run_coroutine_threadsafe(self.agent.sync_file(Path(event.src_path)), self.loop)

    def _increment_ent_points(self, gain=1):
        """Increments ENT points for all active agents in the fleet."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("UPDATE agent_stats SET ent = ent + ?", (gain,))
            conn.commit()
            conn.close()
            logger.info(f"🧠 Fleet indexed new entities (+{gain} ENT).")
        except Exception as e:
            logger.error(f"Failed to update ENT points: {e}")

def start_obsidian_watcher(vault_path=None):
    """Starts the background observer for the Obsidian vault."""
    if vault_path is None:
        from dotenv import load_dotenv
        load_dotenv()
        vault_path = os.getenv("VAULT_PATH", "knowledge_vault/")
        
    if not os.path.exists(vault_path):
        os.makedirs(vault_path, exist_ok=True)
        
    loop = asyncio.new_event_loop()
    
    # Run the loop in a background thread
    from threading import Thread
    thread = Thread(target=loop.run_forever, daemon=True)
    thread.start()
    
    event_handler = ObsidianKnowledgeHandler(vault_path, loop=loop)
    observer = Observer()
    observer.schedule(event_handler, vault_path, recursive=True)
    observer.start()
    logger.info(f"Obsidian Watcher started on {vault_path}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_obsidian_watcher()
