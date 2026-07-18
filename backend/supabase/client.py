"""
PROJECT ZERO — Supabase Client
Complete cloud memory interface with:
- 7-tier memory storage
- Semantic vector search (pgvector)
- Conversation history
- Identity tracking
- Knowledge base
- Task queue
- People/relationship tracking
- Full error recovery
"""

import asyncio
import json
import logging
import os
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger("SupabaseClient")


# ─────────────────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────────────────

@dataclass
class MemoryRecord:
    content: str
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    sender: str = "user"
    emotion: str = "neutral"
    importance: float = 0.5
    expires_days: Optional[int] = None
    session_id: Optional[str] = None
    source: str = "conversation"


@dataclass
class SearchResult:
    id: str
    content: str
    category: str
    emotion: str
    similarity: float
    created_at: str
    tags: List[str] = field(default_factory=list)


@dataclass
class ConversationRecord:
    session_id: str
    message: str
    response: str
    persona: str = "jarvis"
    emotion: str = "neutral"
    intent: str = "conversation"
    language: str = "english"
    sender: str = "user"
    source: str = "api"
    confidence: float = 0.8
    processing_ms: float = 0.0


# ─────────────────────────────────────────────────────────
# EMBEDDER
# ─────────────────────────────────────────────────────────

class LocalEmbedder:
    """
    Local sentence transformer for generating embeddings.
    Uses all-MiniLM-L6-v2 (small, fast, free, 384 dims).
    """

    MODEL_NAME = "all-MiniLM-L6-v2"
    DIMS = 384

    def __init__(self):
        self._model = None
        self._ready = False

    def initialize(self):
        """Load the model"""
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.MODEL_NAME)
            self._ready = True
            logger.info(
                f"✅ Embedder ready ({self.MODEL_NAME})"
            )
        except Exception as e:
            logger.warning(
                f"Embedder not available: {e} "
                f"— semantic search disabled"
            )

    def embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        if not self._ready or not self._model:
            return None
        try:
            vec = self._model.encode(
                text[:512],  # Limit input length
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return vec.tolist()
        except Exception as e:
            logger.debug(f"Embed error: {e}")
            return None

    def embed_batch(
        self, texts: List[str]
    ) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts"""
        if not self._ready or not self._model:
            return [None] * len(texts)
        try:
            vecs = self._model.encode(
                [t[:512] for t in texts],
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return [v.tolist() for v in vecs]
        except Exception as e:
            logger.debug(f"Batch embed error: {e}")
            return [None] * len(texts)

    @property
    def ready(self) -> bool:
        return self._ready


# ─────────────────────────────────────────────────────────
# MAIN CLIENT
# ─────────────────────────────────────────────────────────

class SupabaseMemory:
    """
    Complete Supabase cloud memory client.

    FEATURES:
    - Store conversations, facts, memories
    - Semantic vector search with pgvector
    - Identity tracking (who the user is)
    - Relationship tracking (people)
    - Knowledge base (learned facts)
    - Task queue (automation)
    - Full error recovery (never crashes)
    - Async-safe with executor pool
    - Auto-retry on transient failures
    - Statistics tracking
    """

    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL", "")
        self.key = os.getenv("SUPABASE_KEY", "")
        self.service_key = os.getenv(
            "SUPABASE_SERVICE_KEY", self.key
        )
        self.is_ready = False
        self._client = None
        self._embedder = LocalEmbedder()
        self._stats = {
            "stores": 0,
            "recalls": 0,
            "searches": 0,
            "errors": 0,
            "cache_hits": 0
        }
        # Simple in-memory cache for frequent queries
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._cache_ttl = 300  # 5 minutes

    async def initialize(self):
        """
        Initialize Supabase connection.
        Gracefully handles missing credentials.
        """
        if not self.url or not self.key:
            logger.warning(
                "⚠️  Supabase credentials not set "
                "— running without cloud memory"
            )
            return

        try:
            # Import supabase
            from supabase import create_client
            self._client = create_client(
                self.url, self.service_key or self.key
            )

            # Test the connection
            test = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.table("memories")
                    .select("id")
                    .limit(1)
                    .execute()
            )
            self.is_ready = True
            logger.info("✅ Supabase connected")

        except ImportError:
            logger.error(
                "supabase package not installed. "
                "Run: pip install supabase"
            )
            return
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            return

        # Initialize embedder in background
        await asyncio.get_event_loop().run_in_executor(
            None, self._embedder.initialize
        )

    # ═══════════════════════════════════════════════════
    # STORE METHODS
    # ═══════════════════════════════════════════════════

    async def store_conversation(
        self,
        session_id: str,
        message: str,
        response: str,
        persona: str = "jarvis",
        emotion: str = "neutral",
        sender: str = "user",
        source: str = "api",
        intent: str = "conversation",
        language: str = "english",
        confidence: float = 0.8,
        processing_ms: float = 0.0
    ) -> Optional[str]:
        """
        Store a complete conversation turn.
        Returns the record ID or None on failure.
        """
        if not self.is_ready:
            return None

        record = {
            "session_id": session_id,
            "message": message[:4000],
            "response": response[:4000],
            "persona": persona,
            "emotion": emotion,
            "intent": intent,
            "language": language,
            "sender": sender,
            "source": source,
            "confidence": confidence,
            "processing_ms": processing_ms,
            "created_at": datetime.now().isoformat()
        }

        result = await self._safe_insert(
            "conversations", record
        )
        if result:
            self._stats["stores"] += 1
            return result.get("id")
        return None

    async def store_memory(
        self,
        record: MemoryRecord
    ) -> Optional[str]:
        """
        Store a memory with optional vector embedding.
        Core of the Vault (drop zone).
        """
        if not self.is_ready:
            return None

        # Generate embedding
        embedding = None
        if self._embedder.ready:
            embedding = await asyncio.get_event_loop(
            ).run_in_executor(
                None,
                self._embedder.embed,
                record.content
            )

        # Calculate expiry
        expires_at = None
        if record.expires_days:
            expires_at = (
                datetime.now()
                + timedelta(days=record.expires_days)
            ).isoformat()

        data = {
            "content": record.content[:10000],
            "category": record.category,
            "tags": record.tags,
            "sender": record.sender,
            "emotion": record.emotion,
            "importance": record.importance,
            "source": record.source,
            "session_id": record.session_id,
            "created_at": datetime.now().isoformat()
        }

        if embedding:
            data["embedding"] = embedding
        if expires_at:
            data["expires_at"] = expires_at

        result = await self._safe_insert("memories", data)
        if result:
            self._stats["stores"] += 1
            return result.get("id")
        return None

    async def store_dump(
        self,
        content: str,
        category: str = "general",
        tags: List[str] = None,
        sender: str = "user",
        expires_days: int = None
    ) -> Optional[str]:
        """
        The Vault Drop Zone.
        Simplified interface for quick memory storage.
        """
        record = MemoryRecord(
            content=content,
            category=category,
            tags=tags or [],
            sender=sender,
            expires_days=expires_days,
            source="dump"
        )
        return await self.store_memory(record)

    async def store_fact(
        self,
        fact: str,
        category: str = "general",
        confidence: float = 0.7,
        source: str = "conversation"
    ) -> Optional[str]:
        """Store a learned fact in the knowledge base"""
        if not self.is_ready:
            return None

        embedding = None
        if self._embedder.ready:
            embedding = await asyncio.get_event_loop(
            ).run_in_executor(
                None, self._embedder.embed, fact
            )

        data = {
            "fact": fact[:2000],
            "category": category,
            "confidence": confidence,
            "source": source,
            "updated_at": datetime.now().isoformat()
        }
        if embedding:
            data["embedding"] = embedding

        # Upsert (insert or update if fact exists)
        result = await self._safe_upsert(
            "knowledge", data, on_conflict="fact"
        )
        if result:
            return result.get("id")
        return None

    async def update_identity(
        self,
        attribute: str,
        value: str,
        confidence: float = 0.8,
        source: str = "stated"
    ) -> bool:
        """Update a user identity attribute"""
        if not self.is_ready:
            return False

        data = {
            "attribute": attribute,
            "value": value[:500],
            "confidence": confidence,
            "source": source,
            "updated_at": datetime.now().isoformat()
        }

        result = await self._safe_upsert(
            "identity", data, on_conflict="attribute"
        )
        return result is not None

    async def update_person(
        self,
        name: str,
        relationship: str = None,
        facts: Dict = None,
        phone: str = None
    ) -> bool:
        """Update relationship/people tracking"""
        if not self.is_ready:
            return False

        # Get existing record
        existing = await self._safe_select(
            "people",
            filters={"name": name},
            limit=1
        )

        if existing:
            # Merge facts
            old_facts = existing[0].get("facts", {})
            if isinstance(old_facts, str):
                try:
                    old_facts = json.loads(old_facts)
                except:
                    old_facts = {}
            merged = {**old_facts, **(facts or {})}

            update_data = {
                "facts": merged,
                "interaction_count": (
                    existing[0].get("interaction_count", 0) + 1
                ),
                "last_seen": datetime.now().isoformat()
            }
            if relationship:
                update_data["relationship"] = relationship
            if phone:
                update_data["phone"] = phone

            return await self._safe_update(
                "people", update_data, {"name": name}
            )
        else:
            data = {
                "name": name,
                "relationship": relationship or "unknown",
                "facts": facts or {},
                "phone": phone,
                "interaction_count": 1,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
            result = await self._safe_insert("people", data)
            return result is not None

    async def add_task(
        self,
        title: str,
        description: str = "",
        task_type: str = "general",
        priority: int = 5,
        input_data: Dict = None,
        assigned_agent: str = None
    ) -> Optional[str]:
        """Add a task to the automation queue"""
        if not self.is_ready:
            return None

        data = {
            "title": title[:500],
            "description": description[:2000],
            "task_type": task_type,
            "status": "pending",
            "priority": priority,
            "input_data": input_data or {},
            "assigned_agent": assigned_agent,
            "created_at": datetime.now().isoformat()
        }

        result = await self._safe_insert("tasks", data)
        if result:
            return result.get("id")
        return None

    async def log_system_event(
        self,
        level: str,
        service: str,
        message: str,
        details: Dict = None
    ) -> bool:
        """Log a system event"""
        if not self.is_ready:
            return False

        data = {
            "level": level,
            "service": service,
            "message": message[:2000],
            "details": details or {},
            "created_at": datetime.now().isoformat()
        }

        result = await self._safe_insert("system_logs", data)
        return result is not None

    # ═══════════════════════════════════════════════════
    # RECALL / SEARCH METHODS
    # ═══════════════════════════════════════════════════

    async def semantic_search(
        self,
        query: str,
        limit: int = 5,
        threshold: float = 0.45,
        category: str = None,
        use_cache: bool = True
    ) -> List[SearchResult]:
        """
        Semantic vector search across memories.
        Falls back to keyword search if embedder unavailable.
        """
        if not self.is_ready:
            return []

        self._stats["searches"] += 1

        # Check cache
        cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}:{limit}"
        if use_cache:
            cached = self._get_cache(cache_key)
            if cached is not None:
                self._stats["cache_hits"] += 1
                return cached

        # Try semantic search first
        if self._embedder.ready:
            results = await self._semantic_search_vector(
                query, limit, threshold, category
            )
        else:
            results = await self._semantic_search_text(
                query, limit, category
            )

        # Cache results
        self._set_cache(cache_key, results)
        return results

    async def _semantic_search_vector(
        self,
        query: str,
        limit: int,
        threshold: float,
        category: str = None
    ) -> List[SearchResult]:
        """Vector similarity search using pgvector"""
        # Generate query embedding
        embedding = await asyncio.get_event_loop(
        ).run_in_executor(
            None, self._embedder.embed, query
        )

        if not embedding:
            return await self._semantic_search_text(
                query, limit, category
            )

        try:
            # Call Supabase RPC function
            params = {
                "query_embedding": embedding,
                "match_threshold": threshold,
                "match_count": limit
            }

            result = await asyncio.get_event_loop(
            ).run_in_executor(
                None,
                lambda: self._client.rpc(
                    "search_memories", params
                ).execute()
            )

            records = []
            for row in (result.data or []):
                records.append(SearchResult(
                    id=row.get("id", ""),
                    content=row.get("content", ""),
                    category=row.get("category", "general"),
                    emotion=row.get("emotion", "neutral"),
                    similarity=row.get("similarity", 0.0),
                    created_at=row.get("created_at", ""),
                    tags=row.get("tags", [])
                ))

            return records

        except Exception as e:
            logger.debug(f"Vector search error: {e}")
            # Fallback to text search
            return await self._semantic_search_text(
                query, limit, category
            )

    async def _semantic_search_text(
        self,
        query: str,
        limit: int,
        category: str = None
    ) -> List[SearchResult]:
        """Full-text search fallback"""
        try:
            # Extract keywords
            keywords = [
                w for w in query.lower().split()
                if len(w) > 2
            ][:5]

            if not keywords:
                return []

            # Search with ilike for each keyword
            search_term = keywords[0]

            qb = self._client.table("memories").select(
                "id, content, category, emotion, "
                "created_at, tags, importance"
            ).ilike("content", f"%{search_term}%")

            if category:
                qb = qb.eq("category", category)

            result = await asyncio.get_event_loop(
            ).run_in_executor(
                None,
                lambda: qb.order(
                    "importance", desc=True
                ).limit(limit).execute()
            )

            records = []
            for row in (result.data or []):
                # Calculate basic relevance score
                content_lower = row.get("content", "").lower()
                relevance = sum(
                    1 for kw in keywords
                    if kw in content_lower
                ) / max(len(keywords), 1)

                records.append(SearchResult(
                    id=row.get("id", ""),
                    content=row.get("content", ""),
                    category=row.get("category", "general"),
                    emotion=row.get("emotion", "neutral"),
                    similarity=relevance,
                    created_at=row.get("created_at", ""),
                    tags=row.get("tags", [])
                ))

            # Sort by relevance
            records.sort(key=lambda x: -x.similarity)
            return records

        except Exception as e:
            logger.debug(f"Text search error: {e}")
            return []

    async def get_recent_conversations(
        self,
        session_id: str = None,
        limit: int = 10,
        sender: str = None
    ) -> List[Dict]:
        """Get recent conversation history"""
        if not self.is_ready:
            return []

        try:
            qb = self._client.table("conversations").select(
                "session_id, message, response, persona, "
                "emotion, language, sender, created_at"
            )

            if session_id:
                qb = qb.eq("session_id", session_id)
            if sender:
                qb = qb.eq("sender", sender)

            result = await asyncio.get_event_loop(
            ).run_in_executor(
                None,
                lambda: qb.order(
                    "created_at", desc=True
                ).limit(limit).execute()
            )

            # Return in chronological order
            data = result.data or []
            return list(reversed(data))

        except Exception as e:
            logger.debug(f"Get conversations error: {e}")
            return []

    async def get_identity(
        self, attribute: str = None
    ) -> Dict:
        """Get user identity attributes"""
        if not self.is_ready:
            return {}

        cache_key = f"identity:{attribute or 'all'}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            qb = self._client.table("identity").select(
                "attribute, value, confidence, updated_at"
            )
            if attribute:
                qb = qb.eq("attribute", attribute)

            result = await asyncio.get_event_loop(
            ).run_in_executor(
                None, lambda: qb.execute()
            )

            identity = {}
            for row in (result.data or []):
                identity[row["attribute"]] = {
                    "value": row["value"],
                    "confidence": row["confidence"],
                    "updated_at": row["updated_at"]
                }

            self._set_cache(cache_key, identity, ttl=60)
            return identity

        except Exception as e:
            logger.debug(f"Get identity error: {e}")
            return {}

    async def get_person(
        self, name: str
    ) -> Optional[Dict]:
        """Get relationship info about a person"""
        if not self.is_ready:
            return None

        results = await self._safe_select(
            "people",
            filters={"name": name},
            limit=1
        )
        return results[0] if results else None

    async def get_pending_tasks(
        self,
        task_type: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get pending tasks from queue"""
        if not self.is_ready:
            return []

        try:
            qb = self._client.table("tasks").select(
                "*"
            ).eq("status", "pending")

            if task_type:
                qb = qb.eq("task_type", task_type)

            result = await asyncio.get_event_loop(
            ).run_in_executor(
                None,
                lambda: qb.order(
                    "priority", desc=True
                ).limit(limit).execute()
            )

            return result.data or []

        except Exception as e:
            logger.debug(f"Get tasks error: {e}")
            return []

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        output: Dict = None,
        error: str = None
    ) -> bool:
        """Update task status"""
        if not self.is_ready:
            return False

        update_data = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }

        if status == "running":
            update_data["started_at"] = (
                datetime.now().isoformat()
            )
        elif status in ("completed", "failed"):
            update_data["completed_at"] = (
                datetime.now().isoformat()
            )

        if output:
            update_data["output_data"] = output
        if error:
            update_data["error"] = error[:500]

        return await self._safe_update(
            "tasks", update_data, {"id": task_id}
        )

    async def search_knowledge(
        self, query: str, limit: int = 5
    ) -> List[Dict]:
        """Search the knowledge base"""
        if not self.is_ready:
            return []

        try:
            keywords = query.lower().split()[:3]
            if not keywords:
                return []

            qb = self._client.table("knowledge").select(
                "fact, category, confidence, source, created_at"
            ).ilike("fact", f"%{keywords[0]}%")

            result = await asyncio.get_event_loop(
            ).run_in_executor(
                None,
                lambda: qb.order(
                    "confidence", desc=True
                ).limit(limit).execute()
            )

            return result.data or []

        except Exception as e:
            logger.debug(f"Knowledge search error: {e}")
            return []

    async def get_stats(self) -> Dict:
        """Get memory statistics"""
        if not self.is_ready:
            return {"status": "offline", **self._stats}

        stats = {
            "status": "online",
            "client_stats": self._stats,
            "embedder_ready": self._embedder.ready,
            "cache_size": len(self._cache)
        }

        # Get table counts
        tables = [
            "memories", "conversations",
            "knowledge", "people", "tasks"
        ]
        counts = {}
        for table in tables:
            try:
                result = await asyncio.get_event_loop(
                ).run_in_executor(
                    None,
                    lambda t=table: self._client.table(t)
                        .select("id", count="exact")
                        .execute()
                )
                counts[table] = result.count or 0
            except:
                counts[table] = -1

        stats["counts"] = counts
        return stats

    async def cleanup_expired(self) -> int:
        """Remove expired memories"""
        if not self.is_ready:
            return 0

        try:
            result = await asyncio.get_event_loop(
            ).run_in_executor(
                None,
                lambda: self._client.rpc(
                    "cleanup_expired_memories"
                ).execute()
            )
            count = result.data or 0
            if count > 0:
                logger.info(
                    f"🧹 Cleaned up {count} expired memories"
                )
            return count
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")
            return 0

    # ═══════════════════════════════════════════════════
    # SAFE DATABASE OPERATIONS (with retry)
    # ═══════════════════════════════════════════════════

    async def _safe_insert(
        self, table: str, data: Dict
    ) -> Optional[Dict]:
        """Insert with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await asyncio.get_event_loop(
                ).run_in_executor(
                    None,
                    lambda: self._client.table(table)
                        .insert(data)
                        .execute()
                )
                if result.data:
                    return result.data[0]
                return None
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(
                        self.RETRY_DELAY * (attempt + 1)
                    )
                else:
                    logger.debug(
                        f"Insert {table} failed: {e}"
                    )
                    self._stats["errors"] += 1
                    return None
        return None

    async def _safe_upsert(
        self,
        table: str,
        data: Dict,
        on_conflict: str = "id"
    ) -> Optional[Dict]:
        """Upsert with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                result = await asyncio.get_event_loop(
                ).run_in_executor(
                    None,
                    lambda: self._client.table(table)
                        .upsert(data, on_conflict=on_conflict)
                        .execute()
                )
                if result.data:
                    return result.data[0]
                return None
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(
                        self.RETRY_DELAY * (attempt + 1)
                    )
                else:
                    logger.debug(
                        f"Upsert {table} failed: {e}"
                    )
                    self._stats["errors"] += 1
                    return None
        return None

    async def _safe_update(
        self,
        table: str,
        data: Dict,
        filters: Dict
    ) -> bool:
        """Update with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                qb = self._client.table(table).update(data)
                for key, value in filters.items():
                    qb = qb.eq(key, value)

                await asyncio.get_event_loop(
                ).run_in_executor(
                    None, lambda: qb.execute()
                )
                return True
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(
                        self.RETRY_DELAY * (attempt + 1)
                    )
                else:
                    logger.debug(
                        f"Update {table} failed: {e}"
                    )
                    self._stats["errors"] += 1
                    return False
        return False

    async def _safe_select(
        self,
        table: str,
        columns: str = "*",
        filters: Dict = None,
        limit: int = 10,
        order_by: str = None,
        desc: bool = False
    ) -> List[Dict]:
        """Select with retry logic"""
        for attempt in range(self.MAX_RETRIES):
            try:
                qb = self._client.table(table).select(columns)

                if filters:
                    for key, value in filters.items():
                        qb = qb.eq(key, value)

                if order_by:
                    qb = qb.order(order_by, desc=desc)

                qb = qb.limit(limit)

                result = await asyncio.get_event_loop(
                ).run_in_executor(
                    None, lambda: qb.execute()
                )
                return result.data or []
            except Exception as e:
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(
                        self.RETRY_DELAY * (attempt + 1)
                    )
                else:
                    logger.debug(
                        f"Select {table} failed: {e}"
                    )
                    self._stats["errors"] += 1
                    return []
        return []

    # ═══════════════════════════════════════════════════
    # CACHE METHODS
    # ═══════════════════════════════════════════════════

    def _get_cache(self, key: str) -> Optional[Any]:
        """Get from in-memory cache if not expired"""
        if key in self._cache:
            value, expires = self._cache[key]
            if time.time() < expires:
                return value
            del self._cache[key]
        return None

    def _set_cache(
        self,
        key: str,
        value: Any,
        ttl: int = None
    ):
        """Set in-memory cache"""
        ttl = ttl or self._cache_ttl
        self._cache[key] = (value, time.time() + ttl)

        # Prevent cache from growing too large
        if len(self._cache) > 500:
            # Remove oldest 100 entries
            sorted_keys = sorted(
                self._cache.keys(),
                key=lambda k: self._cache[k][1]
            )
            for k in sorted_keys[:100]:
                del self._cache[k]

    def invalidate_cache(self, prefix: str = None):
        """Invalidate cache entries"""
        if prefix:
            keys = [
                k for k in self._cache.keys()
                if k.startswith(prefix)
            ]
            for k in keys:
                del self._cache[k]
        else:
            self._cache.clear()
