import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from core.base_agent import BaseAgent
from core.message_bus import Channel, Message, Priority

class LearningScheduler(BaseAgent):
    def __init__(self, config: dict):
        super().__init__("LearningScheduler", [Channel.SCHEDULER])
        self.queue_path = Path(config.get("db_paths", {}).get("learning_queue", "arion/data/learning_queue.json"))
        self.vault_path = Path(config.get("db_paths", {}).get("obsidian_vault", "arion/vault"))
        self.ollama_url = config.get("ollama_url", "http://localhost:11434")
        self.model = config.get("model_name", "llama3.1")

    async def run_loop(self):
        # Initial queue check
        await self._ensure_queue_exists()
        
        while self.running:
            # Check for scheduled tasks...
            # For now, we'll just check every hour
            now = datetime.now().strftime("%H:%M")
            
            # 10:00 AM Deep Learning
            if now == "10:00":
                await self.run_daily_learning()
            
            # 10:00 PM Reflection
            if now == "22:00":
                await self._daily_reflection()

            await asyncio.sleep(60) # check every minute

    async def handle_message(self, message: Message):
        if message.action == "add_to_queue":
            await self._add_to_queue(message.payload)
            if message.requires_response:
                await self.respond_to(message, "queued_success", {"title": message.payload.get("title")})
        
        elif message.action == "trigger_learning":
            asyncio.create_task(self.run_daily_learning())

    async def run_daily_learning(self):
        print("[LearningScheduler] Reading: Starting daily learning session...", flush=True)
        queue = await self._get_queue()
        
        pending = [item for item in queue if item["status"] == "queued"]
        if not pending:
            print("[LearningScheduler] Queue empty, nothing to learn today.", flush=True)
            return

        items_learned = []
        for item in pending[:3]: # Learn max 3 items per session to avoid overload
            # Send message to KnowledgeIngestionEngine
            ingest_req = Message(
                from_agent=self.name,
                to_channel=Channel.KNOWLEDGE,
                action="ingest_content",
                payload={
                    "content": item.get("content", ""),
                    "domain": item.get("domain", "general"),
                    "title": item["title"],
                    "source_type": item.get("source_type", "manual")
                },
                requires_response=True
            )
            
            # We don't wait for it here, we let it run.
            # But we update the status in our queue
            item["status"] = "processing"
            await self._save_queue(queue)
            
            res = await self.bus.request(ingest_req, timeout=120)
            if res and res.action == "content_ingested":
                item["status"] = "completed"
                item["completed_at"] = datetime.now().isoformat()
                items_learned.append(item["title"])
            else:
                item["status"] = "failed"
            
            await self._save_queue(queue)
            await asyncio.sleep(5) # Cooldown

        if items_learned:
            await self._daily_reflection(items_learned)

    async def _daily_reflection(self, items: List[str]):
        """Writes a brief reflection journal in the vault."""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        journal_path = self.vault_path / "Memories" / "Learning_Journal" / f"{timestamp}_reflection.md"
        journal_path.parent.mkdir(parents=True, exist_ok=True)
        
        messages = [
            {"role": "system", "content": "You are ARION. Write a brief (2-3 sentence) casual reflection on what you learned today. Mixed English/Telugu (Romanized) style."},
            {"role": "user", "content": f"Today I learned about: {', '.join(items)}"}
        ]
        
        reflection = await self._ollama_request(messages) or "Learned some cool stuff today ra."
        
        content = f"""---
type: learning_reflection
date: {timestamp}
items: {items}
---

# ARION's Daily Reflection — {timestamp}

{reflection}

---
*Stay curious ra.*
"""
        def _write():
            with open(journal_path, "w", encoding="utf-8") as f:
                f.write(content)
        await asyncio.to_thread(_write)
        print(f"[LearningScheduler] Journal: Reflection saved: {journal_path}", flush=True)

    async def _add_to_queue(self, payload: dict):
        queue = await self._get_queue()
        item = {
            "id": str(uuid.uuid4()),
            "title": payload.get("title", "Unknown"),
            "domain": payload.get("domain", "general"),
            "content": payload.get("content", ""),
            "source_type": payload.get("source_type", "manual"),
            "status": "queued",
            "priority": payload.get("priority", 5),
            "added_at": datetime.now().isoformat()
        }
        queue.append(item)
        await self._save_queue(queue)
        print(f"[LearningScheduler] Queued: '{item['title']}'", flush=True)

        if item["priority"] >= 9:
            print(f"[LearningScheduler] High priority item detected. Triggering immediate ingestion.", flush=True)
            asyncio.create_task(self.run_daily_learning())

    async def _get_queue(self) -> list:
        if not self.queue_path.exists(): return []
        try:
            with open(self.queue_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []

    async def _save_queue(self, queue: list):
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.queue_path, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)

    async def _ensure_queue_exists(self):
        if not self.queue_path.exists():
            await self._save_queue([])

    async def _ollama_request(self, messages: list) -> Optional[str]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/chat",
                    json={"model": self.model, "messages": messages, "stream": False}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("message", {}).get("content", "").strip()
        except: return None
