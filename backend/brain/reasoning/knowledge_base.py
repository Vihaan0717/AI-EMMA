"""
KnowledgeBase — Organized, searchable knowledge storage.
Stores facts, procedures, algorithms, and analysis.
Categorized by topic + tags. Supports FTS and semantic-style search.
"""

import sqlite3
import json
import re
import logging
import hashlib
from typing import Optional, Dict, List, Any
from datetime import datetime
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger("JARVIS.KnowledgeBase")

DB_PATH = Path(__file__).parent.parent / "data" / "knowledge.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class KnowledgeBase:
    """
    Structured, long-term knowledge storage for JARVIS.
    Organizes information by:
      - Topic hierarchy  (e.g. programming > python > decorators)
      - Tags             (e.g. #algorithm #sorting #optimization)
      - Source           (ollama / web / user / manual)
      - Content type     (fact / procedure / algorithm / analysis)
    """

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        logger.info(f"✅ KnowledgeBase ready — DB: {DB_PATH}")

    # ═══════════════════════════════════════════════════════════════
    #  DB SETUP
    # ═══════════════════════════════════════════════════════════════

    def _init_db(self):
        c = self.conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                topic        TEXT    NOT NULL,
                content      TEXT    NOT NULL,
                summary      TEXT    DEFAULT '',
                analysis     TEXT    DEFAULT '{}',
                content_type TEXT    DEFAULT 'fact',
                tags         TEXT    DEFAULT '[]',
                source       TEXT    DEFAULT 'unknown',
                relevance    REAL    DEFAULT 0.8,
                access_count INTEGER DEFAULT 0,
                created_at   TEXT    NOT NULL,
                updated_at   TEXT    NOT NULL
            )
        """)

        # Full-text search
        c.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts
            USING fts5(
                topic,
                content,
                tags,
                summary,
                content=knowledge,
                content_rowid=id
            )
        """)

        # Auto-sync triggers
        c.execute("""
            CREATE TRIGGER IF NOT EXISTS knowledge_ai
            AFTER INSERT ON knowledge BEGIN
                INSERT INTO knowledge_fts(rowid, topic, content, tags, summary)
                VALUES (new.id, new.topic, new.content, new.tags, new.summary);
            END
        """)

        c.execute("""
            CREATE TRIGGER IF NOT EXISTS knowledge_au
            AFTER UPDATE ON knowledge BEGIN
                INSERT INTO knowledge_fts(knowledge_fts, rowid, topic, content, tags, summary)
                VALUES ('delete', old.id, old.topic, old.content, old.tags, old.summary);
                INSERT INTO knowledge_fts(rowid, topic, content, tags, summary)
                VALUES (new.id, new.topic, new.content, new.tags, new.summary);
            END
        """)

        # Topic index for browsing
        c.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                topic        TEXT PRIMARY KEY,
                parent_topic TEXT DEFAULT NULL,
                entry_count  INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        """)

        self.conn.commit()

    # ═══════════════════════════════════════════════════════════════
    #  STORE
    # ═══════════════════════════════════════════════════════════════

    def store(
        self,
        topic: str,
        content: str,
        analysis: Dict = None,
        source: str = "unknown",
        tags: List[str] = None,
        content_type: str = "fact",
        summary: str = ""
    ) -> int:
        """
        Store a knowledge entry.
        Returns the row ID of the stored entry.
        """
        tags     = tags     or []
        analysis = analysis or {}
        now      = datetime.utcnow().isoformat()

        # Auto-generate summary if not provided
        if not summary and content:
            summary = self._auto_summarize(content)

        c = self.conn.cursor()
        c.execute("""
            INSERT INTO knowledge
                (topic, content, summary, analysis, content_type,
                 tags, source, relevance, access_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0.8, 0, ?, ?)
        """, (
            topic,
            content,
            summary,
            json.dumps(analysis),
            content_type,
            json.dumps(tags),
            source,
            now, now
        ))
        entry_id = c.lastrowid

        # Update topic index
        c.execute("""
            INSERT INTO topics (topic, entry_count, last_updated)
            VALUES (?, 1, ?)
            ON CONFLICT(topic) DO UPDATE SET
                entry_count = entry_count + 1,
                last_updated = excluded.last_updated
        """, (topic, now))

        self.conn.commit()
        logger.info(
            f"📚 KB stored: topic='{topic}' type={content_type} "
            f"tags={tags} id={entry_id}"
        )
        return entry_id

    # ═══════════════════════════════════════════════════════════════
    #  SEARCH
    # ═══════════════════════════════════════════════════════════════

    def smart_search(self, query: str, limit: int = 5) -> Optional[Dict]:
        """
        Multi-stage search:
        1. FTS5 full-text search
        2. Tag-based search
        3. Topic fuzzy match
        Returns the best result or None.
        """
        # Stage 1: FTS search
        fts_results = self._fts_search(query, limit)

        # Stage 2: Tag search
        tag_results = self._tag_search(query, limit)

        # Merge and deduplicate by id
        seen = set()
        all_results = []
        for r in fts_results + tag_results:
            rid = r.get("id")
            if rid not in seen:
                seen.add(rid)
                all_results.append(r)

        if not all_results:
            return None

        # Score and rank results
        best = self._score_results(query, all_results)
        if best:
            self._bump_access(best["id"])
            return {
                "answer":     best.get("content", ""),
                "summary":    best.get("summary", ""),
                "analysis":   json.loads(best.get("analysis", "{}")),
                "topic":      best.get("topic", ""),
                "tags":       json.loads(best.get("tags", "[]")),
                "source":     best.get("source", ""),
                "relevance":  best.get("_score", 0.75),
                "confidence": best.get("_score", 0.75)
            }
        return None

    def _fts_search(self, query: str, limit: int) -> List[Dict]:
        clean = re.sub(r'[^\w\s]', ' ', query)
        words = [w for w in clean.split() if len(w) > 2]
        if not words:
            return []

        fts_query = " OR ".join(words[:8])
        try:
            rows = self.conn.execute("""
                SELECT k.*, bm25(knowledge_fts) AS bm25_score
                FROM knowledge_fts
                JOIN knowledge k ON knowledge_fts.rowid = k.id
                WHERE knowledge_fts MATCH ?
                ORDER BY bm25_score
                LIMIT ?
            """, (fts_query, limit)).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.debug(f"FTS error: {e}")
            return []

    def _tag_search(self, query: str, limit: int) -> List[Dict]:
        """Search by tags extracted from the query."""
        tags = self._extract_tags_from_query(query)
        if not tags:
            return []

        results = []
        for tag in tags[:3]:
            rows = self.conn.execute(
                "SELECT * FROM knowledge WHERE tags LIKE ? LIMIT ?",
                (f'%"{tag}"%', limit)
            ).fetchall()
            results.extend([dict(r) for r in rows])
        return results

    def _score_results(self, query: str, results: List[Dict]) -> Optional[Dict]:
        """
        Score search results by keyword relevance.
        Returns the best-scoring result.
        """
        query_words = set(re.findall(r'\b\w{3,}\b', query.lower()))
        best_score  = 0.0
        best_result = None

        for r in results:
            text   = f"{r.get('topic','')} {r.get('summary','')} {r.get('content','')}".lower()
            words  = set(re.findall(r'\b\w{3,}\b', text))
            overlap = len(query_words & words)
            score   = overlap / max(len(query_words), 1)

            # Access count boost (popular = more reliable)
            access_boost = min(0.1, r.get("access_count", 0) * 0.01)
            score += access_boost

            if score > best_score:
                best_score  = score
                best_result = {**r, "_score": score}

        if best_result and best_score >= 0.40:
            return best_result
        return None

    # ═══════════════════════════════════════════════════════════════
    #  UTILITIES
    # ═══════════════════════════════════════════════════════════════

    def _auto_summarize(self, content: str) -> str:
        """Create a short summary of the content (first sentence/line)."""
        first_line = content.split('\n')[0].strip()
        if len(first_line) > 100:
            return first_line[:97] + "..."
        return first_line

    def _extract_tags_from_query(self, query: str) -> List[str]:
        """Simple keyword-to-tag mapping."""
        # This could be much smarter
        query = query.lower()
        tags = []
        if "how" in query: tags.append("procedure")
        if "what" in query: tags.append("fact")
        if "algorithm" in query or "step" in query: tags.append("algorithm")
        if "code" in query or "python" in query: tags.append("coding")
        return tags

    def _bump_access(self, entry_id: int):
        self.conn.execute(
            "UPDATE knowledge SET access_count = access_count + 1, updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), entry_id)
        )
        self.conn.commit()

    def count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()
        return row[0] if row else 0

    def get_topics(self, limit: int = 20) -> List[Dict]:
        """Return top topics by entry count."""
        rows = self.conn.execute(
            "SELECT * FROM topics ORDER BY entry_count DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_by_topic(self, topic: str) -> List[Dict]:
        """Retrieve all knowledge for a specific topic."""
        rows = self.conn.execute(
            "SELECT * FROM knowledge WHERE topic = ?", (topic,)
        ).fetchall()
        return [dict(r) for r in rows]
