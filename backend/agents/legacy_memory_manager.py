"""
NEXUS-X OMEGA Memory Manager
5-Tier Human-Like Memory System
Working → Short-Term → Episodic → Semantic → Identity
"""

import asyncio
import json
import sqlite3
import logging
import datetime
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger('MemoryManager')


@dataclass
class Memory:
    content: str
    memory_type: str
    importance: float
    emotion: str
    timestamp: str
    tags: List[str]
    sender: str = "user"
    recalled_count: int = 0


class MemoryManager:
    """
    The complete human-like memory system
    5 tiers just like the human brain
    """

    def __init__(self):
        self.db_path = "data/nexus.db"
        self.working_memory: List[Dict] = []
        self.max_working = 10
        self.session_id = datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

    async def initialize(self):
        """Initialize all memory tiers"""
        await self._init_database()
        await self._init_vector_store()
        await self._load_working_memory()
        logger.info("💾 Memory Manager initialized (5-tier)")

    async def _init_database(self):
        """Initialize SQLite database with all tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Working memory (current session)
        c.execute('''CREATE TABLE IF NOT EXISTS working_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Short-term memory (7 days)
        c.execute('''CREATE TABLE IF NOT EXISTS short_term (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            response TEXT,
            topic TEXT,
            emotion TEXT DEFAULT "neutral",
            importance REAL DEFAULT 0.5,
            sender TEXT DEFAULT "user",
            access_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            tags TEXT
        )''')

        # Episodic memory (forever - important moments)
        c.execute('''CREATE TABLE IF NOT EXISTS episodic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT NOT NULL,
            emotion TEXT,
            importance REAL DEFAULT 0.7,
            people_involved TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_recalled TIMESTAMP,
            recall_count INTEGER DEFAULT 0
        )''')

        # Semantic memory (facts and knowledge)
        c.execute('''CREATE TABLE IF NOT EXISTS semantic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact TEXT NOT NULL,
            category TEXT,
            confidence REAL DEFAULT 0.7,
            source TEXT,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP
        )''')

        # Identity memory (who the user IS)
        c.execute('''CREATE TABLE IF NOT EXISTS identity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attribute TEXT NOT NULL,
            value TEXT NOT NULL,
            confidence REAL DEFAULT 0.8,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP,
            UNIQUE(attribute)
        )''')

        # Patterns table (learned behavior patterns)
        c.execute('''CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT,
            pattern TEXT,
            frequency INTEGER DEFAULT 1,
            success_rate REAL DEFAULT 0.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Feedback table
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id TEXT,
            rating INTEGER,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        conn.commit()
        conn.close()
        logger.info("📊 Database tables initialized")

    async def _init_vector_store(self):
        """Initialize ChromaDB for semantic search"""
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(
                path="data/chromadb"
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name="nexus_memories",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("🔍 Vector store initialized")
        except Exception as e:
            logger.warning(
                f"ChromaDB not available: {e} - using SQLite only"
            )
            self.chroma_client = None
            self.collection = None

    async def _load_working_memory(self):
        """Load current session working memory"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT role, content FROM working_memory
            WHERE session_id = ?
            ORDER BY timestamp ASC
            LIMIT ?
        ''', (self.session_id, self.max_working * 2))
        rows = c.fetchall()
        conn.close()

        self.working_memory = [
            {"role": r[0], "content": r[1]} for r in rows
        ]

    # ═══════════════════════════════════════════════════════
    # STORE METHODS
    # ═══════════════════════════════════════════════════════

    async def store(self, data: Dict):
        """Main store entry point - routes to correct tier"""
        memory_type = data.get("type", "conversation")
        importance = self._calculate_importance(data)

        # Always store in working memory (session context)
        await self._store_working(data)

        # Store in short-term (7 days)
        await self._store_short_term(data, importance)

        # Store in episodic if high emotion or importance
        emotion = data.get("emotion", "neutral")
        if importance > 0.7 or emotion in [
            "joy", "sadness", "anger", "fear", "love", "surprise"
        ]:
            await self._store_episodic(data, importance)

        # Store in vector DB for semantic search
        if self.collection:
            await self._store_vector(data)

        # Extract identity facts
        await self._extract_identity(data)

    async def _store_working(self, data: Dict):
        """Store in working memory (current conversation)"""
        # Add to in-memory list
        if data.get("input"):
            self.working_memory.append({
                "role": "user",
                "content": data["input"]
            })
        if data.get("response"):
            response_content = data["response"]
            if isinstance(response_content, dict):
                response_content = response_content.get(
                    "content", str(response_content)
                )
            self.working_memory.append({
                "role": "assistant",
                "content": str(response_content)
            })

        # Keep within limit
        if len(self.working_memory) > self.max_working * 2:
            self.working_memory = (
                self.working_memory[-(self.max_working * 2):]
            )

        # Persist to DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for entry in [
            ("user", data.get("input", "")),
            ("assistant", str(data.get("response", "")))
        ]:
            if entry[1]:
                c.execute('''
                    INSERT INTO working_memory
                    (session_id, role, content)
                    VALUES (?, ?, ?)
                ''', (self.session_id, entry[0], entry[1][:2000]))
        conn.commit()
        conn.close()

    async def _store_short_term(self, data: Dict, importance: float):
        """Store in short-term memory"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        expires = (
            datetime.datetime.now() + datetime.timedelta(days=7)
        ).isoformat()

        content = data.get("input", data.get("content", ""))
        if not content:
            conn.close()
            return

        c.execute('''
            INSERT INTO short_term
            (content, response, topic, emotion, importance,
             sender, expires_at, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content[:1000],
            str(data.get("response", ""))[:1000],
            data.get("intent", "general"),
            data.get("emotion", "neutral"),
            importance,
            data.get("sender", "user"),
            expires,
            json.dumps(data.get("tags", []))
        ))
        conn.commit()
        conn.close()

    async def _store_episodic(self, data: Dict, importance: float):
        """Store significant moments in episodic memory"""
        content = data.get("input", data.get("content", ""))
        if not content:
            return

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO episodic
            (title, content, emotion, importance)
            VALUES (?, ?, ?, ?)
        ''', (
            content[:100],
            content[:2000],
            data.get("emotion", "neutral"),
            importance
        ))
        conn.commit()
        conn.close()

        # Also save to vault
        await self._save_to_vault(data, "Episodic")

    async def _store_vector(self, data: Dict):
        """Store in ChromaDB for semantic retrieval"""
        if not self.collection:
            return

        content = data.get("input", data.get("content", ""))
        if not content:
            return

        try:
            doc_id = hashlib.md5(
                (content + str(datetime.datetime.now())).encode()
            ).hexdigest()

            self.collection.add(
                documents=[content[:1000]],
                metadatas=[{
                    "type": data.get("type", "conversation"),
                    "emotion": data.get("emotion", "neutral"),
                    "intent": data.get("intent", "general"),
                    "timestamp": str(datetime.datetime.now()),
                    "sender": data.get("sender", "user")
                }],
                ids=[doc_id]
            )
        except Exception as e:
            logger.error(f"Vector store error: {e}")

    async def store_fact(self, fact_data: Dict):
        """Store a learned fact in semantic memory"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO semantic
            (fact, category, confidence, source, last_updated)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            fact_data.get("fact", ""),
            fact_data.get("category", "general"),
            fact_data.get("confidence", 0.7),
            fact_data.get("source", "conversation"),
            datetime.datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

    async def update_identity(
        self, attribute: str, value: str,
        confidence: float = 0.8
    ):
        """Update identity memory about the user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO identity
            (attribute, value, confidence, last_updated)
            VALUES (?, ?, ?, ?)
        ''', (
            attribute, value, confidence,
            datetime.datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

    async def _extract_identity(self, data: Dict):
        """Extract identity facts from conversation"""
        text = data.get("input", "").lower()
        import re

        # Pattern-based identity extraction
        patterns = [
            (r"my name is (\w+)", "name"),
            (r"i am (\d+) years? old", "age"),
            (r"i (like|love|enjoy) (.+?)(?:\.|,|$)", "likes"),
            (r"i (hate|dislike|don't like) (.+?)(?:\.|,|$)", "dislikes"),
            (r"i (live|am from|am in) (.+?)(?:\.|,|$)", "location"),
            (r"i work (at|as|in) (.+?)(?:\.|,|$)", "work"),
            (r"my (birthday|dob) is (.+?)(?:\.|,|$)", "birthday")
        ]

        for pattern, attribute in patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(
                    2 if len(match.groups()) > 1 else 1
                )
                await self.update_identity(attribute, value)

    # ═══════════════════════════════════════════════════════
    # RECALL METHODS
    # ═══════════════════════════════════════════════════════

    async def recall(
        self,
        query: str,
        intent: str = "general",
        limit: int = 5
    ) -> List[Dict]:
        """
        Recall relevant memories from all tiers
        Like a human remembering things
        """
        memories = []

        # 1. Check working memory first (most recent)
        working = self._search_working(query)
        memories.extend(working)

        # 2. Semantic vector search
        if self.collection:
            vector_results = await self._vector_search(query, limit)
            memories.extend(vector_results)

        # 3. SQLite keyword search
        sql_results = await self._sql_search(query, limit)
        memories.extend(sql_results)

        # 4. Identity facts (if personal question)
        if intent in ["personal_info", "memory_recall"]:
            identity = await self._get_identity_facts()
            memories.extend(identity)

        # Deduplicate and sort by relevance
        seen = set()
        unique_memories = []
        for m in memories:
            content = m.get("content", "")[:50]
            if content not in seen:
                seen.add(content)
                unique_memories.append(m)

        return unique_memories[:limit]

    def _search_working(self, query: str) -> List[Dict]:
        """Search working memory"""
        results = []
        query_words = set(query.lower().split())
        for entry in self.working_memory:
            content = entry.get("content", "").lower()
            content_words = set(content.split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                results.append({
                    "content": entry["content"],
                    "type": "working",
                    "relevance": overlap / max(len(query_words), 1),
                    "role": entry.get("role", "unknown")
                })
        return sorted(results, key=lambda x: -x["relevance"])[:3]

    async def _vector_search(
        self, query: str, limit: int
    ) -> List[Dict]:
        """Semantic vector search using ChromaDB"""
        if not self.collection:
            return []
        try:
            count = self.collection.count()
            if count == 0:
                return []

            results = self.collection.query(
                query_texts=[query],
                n_results=min(limit, count)
            )

            memories = []
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for doc, meta, dist in zip(docs, metas, distances):
                relevance = 1 - dist
                if relevance > 0.45:
                    memories.append({
                        "content": doc,
                        "type": "semantic",
                        "relevance": relevance,
                        "emotion": meta.get("emotion", "neutral"),
                        "timestamp": meta.get("timestamp", "")
                    })
            return memories
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

    async def _sql_search(self, query: str, limit: int) -> List[Dict]:
        """Keyword search using SQLite"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        search_term = f"%{query}%"
        c.execute('''
            SELECT content, created_at, emotion, importance, 'short_term' as source
            FROM short_term
            WHERE content LIKE ?
            UNION ALL
            SELECT content, created_at, emotion, importance, 'episodic' as source
            FROM episodic
            WHERE content LIKE ?
            ORDER BY importance DESC
            LIMIT ?
        ''', (search_term, search_term, limit))
        
        rows = c.fetchall()
        conn.close()
        
        return [{
            "content": r[0],
            "timestamp": r[1],
            "emotion": r[2],
            "relevance": r[3],
            "type": r[4]
        } for r in rows]

    async def _get_identity_facts(self) -> List[Dict]:
        """Recall identity facts"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT attribute, value FROM identity')
        rows = c.fetchall()
        conn.close()
        
        return [{
            "content": f"The user's {r[0]} is {r[1]}",
            "type": "identity",
            "relevance": 1.0
        } for r in rows]

    async def _calculate_importance(self, data: Dict) -> float:
        """Calculate memory importance"""
        importance = 0.5
        text = data.get("input", "").lower()
        
        critical_words = ["remember", "important", "never forget", "birthday", "password", "key", "urgent"]
        if any(w in text for w in critical_words):
            importance += 0.2
            
        if data.get("emotion") not in ["neutral", ""]:
            importance += 0.1
            
        return min(1.0, importance)

    async def _save_to_vault(self, data: Dict, category: str):
        """Save to Obsidian Knowledge Vault"""
        vault_path = Path(f"knowledge_vault/Brain/{category}")
        vault_path.mkdir(parents=True, exist_ok=True)
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{hashlib.md5(data.get('input', '').encode()).hexdigest()[:8]}.md"
        
        content = f"""# Memory: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Emotion**: {data.get('emotion', 'neutral')}
- **Intent**: {data.get('intent', 'general')}

## Content
{data.get('input', '')}

## Nexus Response
{data.get('response', '')}
"""
        try:
            with open(vault_path / filename, "w") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Vault save error: {e}")

    async def save_all(self):
        """Save everything before shutdown"""
        logger.info("💾 Persistence cycle complete")
