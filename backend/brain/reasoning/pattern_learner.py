"""
PatternLearner — Learns patterns, algorithms, and steps.
Uses TF-IDF cosine similarity + SQLite FTS5 for fast lookup.
No AI model. Pure mathematics.
"""

import sqlite3
import json
import math
import re
import logging
import hashlib
from typing import Optional, Dict, List, Any
from datetime import datetime
from collections import Counter
from pathlib import Path

logger = logging.getLogger("JARVIS.PatternLearner")

# ── DB location ──────────────────────────────────────────────────
DB_PATH = Path(__file__).parent.parent / "data" / "patterns.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class PatternLearner:
    """
    Learns and recognizes patterns using TF-IDF cosine similarity.
    Stores: query patterns, algorithms, steps, tags, frequency.
    Improves match quality with every interaction.
    """

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self._tfidf_cache: Dict[str, Dict[str, float]] = {}
        logger.info(f"✅ PatternLearner ready — DB: {DB_PATH}")

    # ═══════════════════════════════════════════════════════════════
    #  DB SETUP
    # ═══════════════════════════════════════════════════════════════

    def _init_db(self):
        """Create all tables if they don't exist."""
        c = self.conn.cursor()

        # Main patterns table
        c.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash  TEXT    UNIQUE NOT NULL,
                query_text  TEXT    NOT NULL,
                answer      TEXT    NOT NULL,
                analysis    TEXT    DEFAULT '{}',
                algorithm   TEXT    DEFAULT NULL,
                steps       TEXT    DEFAULT '[]',
                tags        TEXT    DEFAULT '[]',
                source      TEXT    DEFAULT 'unknown',
                confidence  REAL    DEFAULT 0.85,
                hit_count   INTEGER DEFAULT 0,
                created_at  TEXT    NOT NULL,
                last_used   TEXT    NOT NULL
            )
        """)

        # Full-text search virtual table
        c.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts
            USING fts5(
                query_hash UNINDEXED,
                query_text,
                tags,
                algorithm,
                content=patterns,
                content_rowid=id
            )
        """)

        # Trigger: keep FTS in sync on INSERT
        c.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_ai
            AFTER INSERT ON patterns BEGIN
                INSERT INTO patterns_fts(rowid, query_hash, query_text, tags, algorithm)
                VALUES (new.id, new.query_hash, new.query_text, new.tags, new.algorithm);
            END
        """)

        # Trigger: keep FTS in sync on UPDATE
        c.execute("""
            CREATE TRIGGER IF NOT EXISTS patterns_au
            AFTER UPDATE ON patterns BEGIN
                INSERT INTO patterns_fts(patterns_fts, rowid, query_hash, query_text, tags, algorithm)
                VALUES ('delete', old.id, old.query_hash, old.query_text, old.tags, old.algorithm);
                INSERT INTO patterns_fts(rowid, query_hash, query_text, tags, algorithm)
                VALUES (new.id, new.query_hash, new.query_text, new.tags, new.algorithm);
            END
        """)

        # Frequency table — tracks what topics come up most
        c.execute("""
            CREATE TABLE IF NOT EXISTS topic_frequency (
                topic       TEXT PRIMARY KEY,
                count       INTEGER DEFAULT 1,
                last_seen   TEXT NOT NULL
            )
        """)

        self.conn.commit()

    # ═══════════════════════════════════════════════════════════════
    #  STORE
    # ═══════════════════════════════════════════════════════════════

    def store_pattern(
        self,
        query: str,
        response: Dict,
        source: str = "unknown",
        tags: List[str] = None,
        algorithm: Optional[str] = None,
        steps: List[str] = None
    ) -> bool:
        """
        Store a query-response pair as a learnable pattern.
        If the same query hash exists, update the hit count instead.
        """
        tags  = tags  or []
        steps = steps or []
        qhash = self._hash(query)
        now   = datetime.utcnow().isoformat()

        try:
            c = self.conn.cursor()

            # Check if it already exists
            existing = c.execute(
                "SELECT id, hit_count FROM patterns WHERE query_hash = ?", (qhash,)
            ).fetchone()

            if existing:
                # Update — reinforce the pattern
                c.execute("""
                    UPDATE patterns
                    SET hit_count = hit_count + 1,
                        last_used = ?,
                        confidence = MIN(0.99, confidence + 0.01)
                    WHERE query_hash = ?
                """, (now, qhash))
                logger.debug(f"♻️ Pattern reinforced: {query[:50]}")
            else:
                # Insert new pattern
                c.execute("""
                    INSERT INTO patterns
                        (query_hash, query_text, answer, analysis, algorithm,
                         steps, tags, source, confidence, hit_count,
                         created_at, last_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """, (
                    qhash,
                    query,
                    response.get("answer", ""),
                    json.dumps(response.get("analysis", {})),
                    algorithm,
                    json.dumps(steps),
                    json.dumps(tags),
                    source,
                    response.get("confidence", 0.85),
                    now, now
                ))
                logger.info(f"✅ New pattern stored: '{query[:50]}' | tags={tags}")

            # Track topic frequency
            topic = tags[0] if tags else self._extract_main_topic(query)
            c.execute("""
                INSERT INTO topic_frequency (topic, count, last_seen)
                VALUES (?, 1, ?)
                ON CONFLICT(topic) DO UPDATE SET
                    count = count + 1,
                    last_seen = excluded.last_seen
            """, (topic, now))

            self.conn.commit()
            # Clear TF-IDF cache so new pattern is included next search
            self._tfidf_cache.clear()
            return True

        except Exception as e:
            logger.error(f"Store pattern failed: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════
    #  FIND
    # ═══════════════════════════════════════════════════════════════

    def find_best_match(self, query: str) -> Optional[Dict]:
        """
        Find the best matching pattern using a 3-stage approach:
          1. Exact hash match (instant)
          2. FTS5 keyword match (fast)
          3. TF-IDF cosine similarity (accurate)
        Returns the best result or None.
        """
        # Stage 1: Exact match
        exact = self._exact_match(query)
        if exact:
            return exact

        # Stage 2: FTS keyword candidates
        candidates = self._fts_search(query, limit=20)
        if not candidates:
            return None

        # Stage 3: TF-IDF ranking of candidates
        best = self._tfidf_rank(query, candidates)
        return best

    def _exact_match(self, query: str) -> Optional[Dict]:
        qhash = self._hash(query)
        row = self.conn.execute(
            "SELECT * FROM patterns WHERE query_hash = ?", (qhash,)
        ).fetchone()
        if row:
            self._bump_hit(row["id"])
            return self._row_to_dict(row, confidence=0.99)
        return None

    def _fts_search(self, query: str, limit: int = 20) -> List[Dict]:
        """Full-text search for candidate patterns."""
        clean = self._clean_for_fts(query)
        if not clean:
            return []
        try:
            rows = self.conn.execute("""
                SELECT p.*, bm25(patterns_fts) AS fts_score
                FROM patterns_fts
                JOIN patterns p ON patterns_fts.rowid = p.id
                WHERE patterns_fts MATCH ?
                ORDER BY fts_score
                LIMIT ?
            """, (clean, limit)).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.debug(f"FTS search error (non-critical): {e}")
            # Fallback: simple LIKE search
            like = f"%{query[:30]}%"
            rows = self.conn.execute(
                "SELECT * FROM patterns WHERE query_text LIKE ? LIMIT ?",
                (like, limit)
            ).fetchall()
            return [dict(r) for r in rows]

    def _tfidf_rank(
        self, query: str, candidates: List[Dict]
    ) -> Optional[Dict]:
        """
        Rank candidates by TF-IDF cosine similarity.
        Returns best match above threshold or None.
        """
        if not candidates:
            return None

        query_vec = self._tfidf_vector(query)
        best_score = 0.0
        best_candidate = None

        for cand in candidates:
            cand_vec = self._tfidf_vector(cand["query_text"])
            score = self._cosine_similarity(query_vec, cand_vec)

            # Boost score by hit frequency (popular answers are more reliable)
            hit_boost = min(0.05, cand.get("hit_count", 0) * 0.005)
            adjusted_score = score + hit_boost

            if adjusted_score > best_score:
                best_score = adjusted_score
                best_candidate = cand

        if best_candidate and best_score >= 0.60:
            self._bump_hit(best_candidate["id"])
            return self._row_to_dict(best_candidate, confidence=best_score)

        return None

    # ═══════════════════════════════════════════════════════════════
    #  TF-IDF ENGINE
    # ═══════════════════════════════════════════════════════════════

    def _tfidf_vector(self, text: str) -> Dict[str, float]:
        """Compute TF-IDF vector for a text string."""
        if text in self._tfidf_cache:
            return self._tfidf_cache[text]

        tokens   = self._tokenize(text)
        tf       = Counter(tokens)
        total    = len(tokens) or 1
        idf      = self._get_idf()

        vector = {
            term: (count / total) * idf.get(term, 1.0)
            for term, count in tf.items()
        }
        self._tfidf_cache[text] = vector
        return vector

    def _get_idf(self) -> Dict[str, float]:
        """
        Compute Inverse Document Frequency from stored patterns.
        Cached for performance.
        """
        if hasattr(self, "_idf_cache") and self._idf_cache:
            return self._idf_cache

        rows = self.conn.execute(
            "SELECT query_text FROM patterns"
        ).fetchall()
        N = len(rows) + 1  # +1 to avoid div by zero

        doc_freq: Dict[str, int] = Counter()
        for row in rows:
            unique_terms = set(self._tokenize(row[0]))
            for term in unique_terms:
                doc_freq[term] += 1

        self._idf_cache = {
            term: math.log(N / (freq + 1))
            for term, freq in doc_freq.items()
        }
        return self._idf_cache

    @staticmethod
    def _cosine_similarity(v1: Dict, v2: Dict) -> float:
        """Cosine similarity between two TF-IDF vectors."""
        common = set(v1.keys()) & set(v2.keys())
        if not common:
            return 0.0

        dot    = sum(v1[t] * v2[t] for t in common)
        norm1  = math.sqrt(sum(x ** 2 for x in v1.values()))
        norm2  = math.sqrt(sum(x ** 2 for x in v2.values()))

        denom = norm1 * norm2
        return dot / denom if denom > 0 else 0.0

    # ═══════════════════════════════════════════════════════════════
    #  UTILITIES
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Lowercase, strip punctuation, split into meaningful tokens."""
        text   = text.lower()
        tokens = re.findall(r'\b[a-z][a-z0-9_]{1,}\b', text)
        # Remove stopwords
        stops  = {
            "the","a","an","is","it","in","on","at","to","for",
            "of","and","or","but","with","this","that","are","was",
            "be","by","as","from","what","how","why","when","where",
            "can","do","does","did","has","have","had","will","would",
            "should","could","may","might","i","we","you","he","she",
            "they","them","their","our","my","your","his","her"
        }
        return [t for t in tokens if t not in stops and len(t) > 1]

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode()).hexdigest()[:16]

    @staticmethod
    def _clean_for_fts(text: str) -> str:
        """Clean text for FTS5 MATCH query."""
        # Remove special FTS characters
        clean = re.sub(r'[^\w\s]', ' ', text)
        words = [w for w in clean.split() if len(w) > 2]
        return " ".join(words[:10])  # FTS5 works best with ≤10 terms

    @staticmethod
    def _extract_main_topic(query: str) -> str:
        """Simple heuristic to extract a topic from a query."""
        # Remove question words
        q = re.sub(
            r'^(what|how|why|when|where|who|which|can|is|are|does)\s+',
            '', query.lower()
        ).strip()
        return q[:40]

    def _bump_hit(self, pattern_id: int):
        """Increment hit counter for a pattern."""
        self.conn.execute(
            "UPDATE patterns SET hit_count = hit_count + 1, "
            "last_used = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), pattern_id)
        )
        self.conn.commit()

    def _row_to_dict(self, row, confidence: float = None) -> Dict:
        """Convert a DB row to a clean response dict."""
        d = dict(row) if not isinstance(row, dict) else row
        return {
            "answer":     d.get("answer", ""),
            "analysis":   json.loads(d.get("analysis", "{}")),
            "algorithm":  d.get("algorithm"),
            "steps":      json.loads(d.get("steps", "[]")),
            "tags":       json.loads(d.get("tags", "[]")),
            "source":     d.get("source", "pattern"),
            "confidence": confidence if confidence is not None else d.get("confidence", 0.85),
            "hit_count":  d.get("hit_count", 0)
        }

    def count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) FROM patterns").fetchone()
        return row[0] if row else 0

    def top_patterns(self, limit: int = 10) -> List[Dict]:
        """Return the most frequently used patterns."""
        rows = self.conn.execute(
            "SELECT query_text, hit_count, tags, source "
            "FROM patterns ORDER BY hit_count DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
