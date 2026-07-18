"""
MemoryManager — ARION's Organized Brain Storage.

Three-tier memory system:
- ShortTerm: Recent raw data, expires in 7 days
- LongTerm: Consolidated patterns and confirmed facts  
- Episodic: Specific memorable events, always kept

All memories are linked to each other using Obsidian [[wikilinks]].
The graph view shows a meaningful web, not random date blobs.
"""

import os
import time
import asyncio
import sqlite3
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.base_agent import BaseAgent
from core.message_bus import Channel, Message, Priority
from brain.vault_brain import VaultBrain

class MemoryManager(BaseAgent):

    VAULT = Path("arion/vault")

    # Memory tier paths
    SHORT_TERM  = VAULT / "Memory" / "ShortTerm"
    LONG_TERM   = VAULT / "Memory" / "LongTerm"
    EPISODIC    = VAULT / "Memory" / "Episodic"
    SEMANTIC    = VAULT / "Memory" / "Semantic"
    WORKING     = VAULT / "Memory" / "Working"
    PEOPLE      = VAULT / "People"
    CONNECTIONS = VAULT / "Connections"

    # How long short-term memories live before consolidation
    SHORT_TERM_EXPIRY_DAYS = 7

    def __init__(self, db_paths: dict):
        super().__init__("MemoryManager", [Channel.MEMORY])
        self.sqlite_path = db_paths.get("sqlite", "arion/data/memory.db")
        self.chroma_path = db_paths.get("chroma", "arion/data/chromadb")
        self.vault_path  = Path(db_paths.get("obsidian_vault", "arion/vault"))
        
        self.vault_brain = VaultBrain(vault_path=str(self.vault_path))
        self.chroma_client = None
        self.collection    = None
        self.slang_collection = None
        self.file_locks: Dict[str, asyncio.Lock] = {}

        self._ensure_vault_structure()
        print("[MemoryManager] Memory system initialized.", flush=True)

    def _ensure_vault_structure(self):
        """Creates all required vault folders."""
        folders = [
            self.SHORT_TERM,
            self.LONG_TERM,
            self.EPISODIC,
            self.SEMANTIC,
            self.WORKING,
            self.PEOPLE / "Owner",
            self.PEOPLE / "Contacts",
            self.CONNECTIONS / "Themes",
            self.CONNECTIONS / "Patterns",
            self.VAULT / "Knowledge" / "Books",
            self.VAULT / "Knowledge" / "Movies",
            self.VAULT / "Knowledge" / "Music",
            self.VAULT / "Knowledge" / "Anime",
            self.VAULT / "Knowledge" / "Philosophy",
            self.VAULT / "Knowledge" / "History",
            self.VAULT / "Knowledge" / "Religion",
            self.VAULT / "Knowledge" / "Science",
            self.VAULT / "Knowledge" / "Psychology",
            self.VAULT / "Knowledge" / "Technology",
            self.VAULT / "Brain" / "Working",
            self.VAULT / "Brain" / "ShortTerm",
            self.VAULT / "Brain" / "LongTerm",
            self.VAULT / "Brain" / "Episodic",
            self.VAULT / "Brain" / "Semantic",
            self.VAULT / "Brain" / "Patterns",
            self.VAULT / "Agent_Self" / "Persona",
            self.VAULT / "Agent_Self" / "Learning_Journal",
            self.VAULT / "Agent_Self" / "Feedback",
        ]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)

    # ── Initialization ───────────────────────────────────────────────

    async def run_loop(self):
        await self._init_sqlite()
        await self._init_chroma()
        
        # Periodic consolidation task
        asyncio.create_task(self._consolidation_scanner())
        
        while self.running:
            msg = await self.get_next_message(timeout=0.5)
            if msg:
                await self.handle_message(msg)

    async def _init_sqlite(self):
        os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
        def _setup():
            conn = sqlite3.connect(self.sqlite_path)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY, contact TEXT, role TEXT, content TEXT, 
                timestamp REAL, tier INTEGER, emotion TEXT, promoted INTEGER DEFAULT 0
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS people_metadata (
                contact TEXT PRIMARY KEY, last_seen REAL, relationship TEXT, 
                bio TEXT, style_notes TEXT, intent_avg REAL DEFAULT 2.0
            )''')
            conn.commit()
            conn.close()
        await asyncio.to_thread(_setup)

    async def _init_chroma(self):
        os.makedirs(self.chroma_path, exist_ok=True)
        def _setup_chroma():
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
            self.collection    = self.chroma_client.get_or_create_collection(name="memory_vectors")
            self.slang_collection = self.chroma_client.get_or_create_collection(name="slang_vault")
            self._seed_slang_vault()
        try:
            await asyncio.to_thread(_setup_chroma)
        except Exception as e:
            print(f"[MemoryManager] ChromaDB Init Error: {e}")

    def _seed_slang_vault(self):
        """Seeds the vector vault with BOTH slang dictionary AND general cultural vocabulary."""
        sources = [
            ("arion/data/culture/slang_dictionary.json", "slang"),
            ("arion/config/vocabulary_telugu.json", "telugu"),
            ("arion/config/vocabulary_hindi.json", "hindi")
        ]
        
        documents, metadatas, ids = [], [], []
        
        for path, source_type in sources:
            if not os.path.exists(path): continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if source_type == "slang":
                    for i, entry in enumerate(data):
                        word = entry.get("word", "")
                        if not word: continue
                        documents.append(word)
                        metadatas.append({
                            "language":  entry.get("language", "unknown"),
                            "meaning":   entry.get("meaning", ""),
                            "strategy":  entry.get("strategy", "mirror")
                        })
                        ids.append(f"slang_{i}")
                else:
                    # General vocabulary files are structured by category
                    for category, entries in data.items():
                        if category == "meta": continue
                        if isinstance(entries, dict):
                            for word, meaning in entries.items():
                                documents.append(word)
                                metadatas.append({
                                    "language":  source_type,
                                    "meaning":   meaning,
                                    "category": category
                                })
                                ids.append(f"vocab_{source_type}_{category}_{word}")
            except Exception as e:
                print(f"[MemoryManager] Seed error for {path}: {e}")

        if documents:
            try:
                self.slang_collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
                print(f"[MemoryManager] Indexed {len(documents)} cultural tokens in slang_vault.", flush=True)
            except Exception as e:
                print(f"[MemoryManager] Upsert error: {e}")

    # ── Message Handler ───────────────────────────────────────────────

    async def handle_message(self, message: Message):
        action = message.action

        if action == "store_conversation":
            await self._store_conversation(message.payload)

        elif action == "decode_slang":
            result = await self._decode_slang(message.payload)
            if message.requires_response:
                await self.respond_to(message, "slang_decoded", result)

        elif action == "get_person_ctx":
            result = await self._get_person_ctx(message.payload)
            if message.requires_response:
                await self.respond_to(message, "person_ctx", result)

        elif action == "get_recent_context":
            result = await self._get_recent_context(message.payload)
            if message.requires_response:
                await self.respond_to(message, "recent_context", result)

        elif action == "write_vault":
            await self._write_vault(message.payload)

        elif action == "store_feedback":
            await self._store_feedback(message.payload)
            
        elif action == "store_emotion":
            await self._store_emotion(message.payload)

    # ────────────────────────────────────────────────────────────────────
    # SHORT TERM MEMORY
    # Organized by TOPIC not by DATE
    # ────────────────────────────────────────────────────────────────────

    async def _store_conversation(self, payload: dict):
        contact  = self._safe_name(payload.get("contact", "unknown"))
        role     = payload.get("role", "user")
        content  = payload.get("content", "")
        emotion  = payload.get("emotion", "")
        intent   = payload.get("intent", "")
        dialect  = payload.get("dialect", "general")
        tier     = int(payload.get("tier", 1))
        ts       = payload.get("timestamp", time.time())
        now      = datetime.fromtimestamp(ts)

        # 1. Update SQLite (Working Database)
        await self._sqlite_insert_conversation(contact, role, content, ts, tier, emotion)

        # 2. Determine topic from intent/content
        topic = self._classify_topic(content, intent)

        # 3. Update Working Memory (Markdown)
        # Updated: Offload synchronous vault writes to threads to prevent loop hang
        await asyncio.to_thread(self.vault_brain.update_working_memory, contact, role, content, emotion, topic)
        
        # 4. Update Person Profile
        if contact != "unknown":
            await self._update_person_profile(contact, role, content, emotion, intent, dialect, topic, now)

        # 5. Store Episode if significant
        if tier >= 3 or emotion in ["frustrated", "sad", "excited"]:
            await asyncio.to_thread(self.vault_brain.write_episodic,
                contact=contact,
                event_description=f"{contact} expressed {emotion} about {topic}",
                full_content=content,
                emotion=emotion
            )

    async def _sqlite_insert_conversation(self, contact, role, content, ts, tier, emotion):
        def _write():
            conn = sqlite3.connect(self.sqlite_path)
            mid = f"{int(ts*1000)}_{contact}"
            conn.execute(
                "INSERT OR REPLACE INTO conversations (id, contact, role, content, timestamp, tier, emotion) VALUES (?,?,?,?,?,?,?)",
                (mid, contact, role, content, ts, tier, emotion)
            )
            conn.commit()
            conn.close()
        
        await asyncio.to_thread(_write)

    # ────────────────────────────────────────────────────────────────────
    # PERSON PROFILES
    # ────────────────────────────────────────────────────────────────────

    async def _update_person_profile(self, contact, role, content, emotion, intent, dialect, topic, timestamp):
        is_owner = contact in ["owner", "919154716156", "owner_telegram"]
        folder = self.PEOPLE / ("Owner" if is_owner else f"Contacts/{contact}")
        folder.mkdir(parents=True, exist_ok=True)
        profile_path = folder / "Profile.md"

        data = await self._load_profile_data(profile_path)
        data["total_interactions"] = data.get("total_interactions", 0) + 1
        data["last_seen"] = timestamp.isoformat()
        data["dialects_used"] = list(set(data.get("dialects_used", []) + [dialect]))

        topics = data.get("topics_discussed", {})
        topics[topic] = topics.get(topic, 0) + 1
        data["topics_discussed"] = topics

        emotions = data.get("emotions_observed", {})
        if emotion:
            emotions[emotion] = emotions.get(emotion, 0) + 1
            data["emotions_observed"] = emotions

        recent = data.get("recent_topics", [])
        recent.append({"topic": topic, "emotion": emotion, "timestamp": timestamp.isoformat()[:16], "snippet": content[:80]})
        data["recent_topics"] = recent[-20:]

        # Updated: Offload synchronous vault profile writes to threads
        await asyncio.to_thread(self.vault_brain.write_person_profile, contact, data)
        
        # Update Topic-specific ShortTerm file
        if topic != "general" and len(content) > 10:
            await asyncio.to_thread(self.vault_brain.write_short_term, contact, topic, content, emotion)

    # ────────────────────────────────────────────────────────────────────
    # EPISODIC / CONSOLIDATION
    # ────────────────────────────────────────────────────────────────────

    async def _consolidation_scanner(self):
        """Runs once an hour to promote short-term to long-term."""
        while self.running:
            await asyncio.sleep(3600)
            now = datetime.now()
            print("[MemoryManager] 🔄 Scanning for consolidation candidates...", flush=True)
            for st_file in self.SHORT_TERM.glob("*.md"):
                try:
                    # Basic logic: if 10+ entries, promote to LongTerm pattern
                    text = st_file.read_text(encoding="utf-8")
                    if text.count("**20") >= 10:
                        parts = st_file.stem.split("_", 1)
                        if len(parts) == 2:
                            await self._promote_to_longterm(parts[0], parts[1], text)
                            st_file.unlink() # Cleanup promoted
                except Exception as e:
                    print(f"[MemoryManager] Consolidation error: {e}")

    async def _promote_to_longterm(self, contact, topic, content):
        path = self.LONG_TERM / f"{contact}_{topic}_pattern.md"
        # Extract a simple 'pattern' summary (placeholder for now)
        summary = f"Consistent discussion about {topic}."
        content_md = f"""---
type: long_term_memory
contact: {contact}
topic: {topic}
promoted: {datetime.now().isoformat()}
---

# Long Term Pattern — {contact} / {topic}

{summary}

## Source Context
{content[:1000]}...
"""
        path.write_text(content_md, encoding="utf-8")

    # ────────────────────────────────────────────────────────────────────
    # LEGACY / SHARED ACTIONS
    # ────────────────────────────────────────────────────────────────────

    async def _write_vault(self, payload: dict):
        rel_path = payload.get("path", "")
        content = payload.get("content", "")
        if not rel_path or not content: return
        
        full_path = self.vault_path / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with self._get_lock(str(full_path)):
            def _write():
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
            await asyncio.to_thread(_write)

    async def _decode_slang(self, payload: dict) -> dict:
        tokens = payload.get("tokens", [])
        decoded = {}
        for token in tokens:
            if not token: continue
            res = await self._chroma_lookup(token)
            if res: decoded[token] = res
        return {"decoded": decoded}

    async def _chroma_lookup(self, token: str) -> Optional[dict]:
        if not self.slang_collection: return None
        try:
            results = self.slang_collection.query(query_texts=[token], n_results=1)
            if results["documents"] and results["distances"][0][0] < 0.2:
                return results["metadatas"][0][0]
        except: pass
        return None

    # ────────────────────────────────────────────────────────────────────
    # HELPERS
    # ────────────────────────────────────────────────────────────────────

    def _safe_name(self, name: str) -> str:
        name = name.split("@")[0]
        name = re.sub(r'[<>:"/\\|?*.\s]+', '_', name)
        return name.strip("_")[:50] or "unknown"

    def _classify_topic(self, content: str, intent: str) -> str:
        content_lower = content.lower()
        mapping = {
            "family": ["amma", "nanna", "sister", "brother", "family", "akka", "anna"],
            "work": ["work", "office", "project", "deadline", "client"],
            "health": ["sick", "fever", "gym", "health", "tired"],
            "emotions": ["sad", "happy", "stressed", "angry"],
            "entertainment": ["movie", "song", "game", "anime"],
            "daily": ["food", "lunch", "eating", "home"]
        }
        for topic, keywords in mapping.items():
            if any(k in content_lower for k in keywords): return topic
        return intent.replace(" ", "_") if intent else "general"

    async def _load_profile_data(self, path: Path) -> dict:
        if not path.exists(): return {}
        content = path.read_text(encoding="utf-8")
        data = {}
        m = re.search(r"total_interactions: (\d+)", content)
        if m: data["total_interactions"] = int(m.group(1))
        m = re.search(r"last_seen: (.+)", content)
        if m: data["last_seen"] = m.group(1).strip()
        return data

    async def _get_person_ctx(self, payload: dict) -> dict:
        contact = self._safe_name(payload.get("contact", ""))
        profile_path = self.PEOPLE / ("Owner/Profile.md" if contact in ["owner", "919154716156"] else f"Contacts/{contact}/Profile.md")
        if not profile_path.exists(): return {"relationship": "unknown", "style": ""}
        # Basic context for orchestrator
        return {"relationship": "owner" if "owner" in contact or "9191" in contact else "contact"}

    async def _get_recent_context(self, payload: dict) -> dict:
        contact = self._safe_name(payload.get("contact", ""))
        path = self.WORKING / f"{contact}.md"
        if not path.exists(): return {"context": ""}
        return {"context": path.read_text(encoding="utf-8")[-2000:]}

    async def _store_feedback(self, payload: dict):
        feedback = payload.get("feedback", "")
        self.vault_brain.write_episodic(
            contact="owner",
            event_description="Owner provided feedback",
            full_content=feedback,
            emotion="neutral",
            related_links=["Agent_Self/Feedback/Feedback_Log"]
        )

    async def _store_emotion(self, payload: dict):
        self.vault_brain.write_episodic(
            contact=payload.get("contact", "unknown"),
            event_description=f"Significant emotional moment: {payload.get('emotion')}",
            full_content=payload.get("content", ""),
            emotion=payload.get("emotion", "neutral")
        )

    def _get_lock(self, key: str) -> asyncio.Lock:
        if key not in self.file_locks: self.file_locks[key] = asyncio.Lock()
        return self.file_locks[key]
