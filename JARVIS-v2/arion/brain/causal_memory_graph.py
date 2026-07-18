"""
arion/brain/causal_memory_graph.py
====================================
ARION 3.0 — Causal Memory Graph (Phase 2)

Pure SQLite graph. No Neo4j dependency.
Records what happened, WHY it happened, and what worked.

Schema:
  exchanges       — every (user_message, arion_reply) pair
  causal_nodes    — entities: emotions, topics, events, decisions
  causal_edges    — relationships: CAUSED, FELT, LED_TO, RESOLVED_BY
  patterns        — learned: "when X is Y, response style Z works N times"

Key insight: When Rohit is anxious about work and ARION responds with
"chill rey" and Rohit's NEXT message is calmer → record that as a success.
Over 10 such cycles: a PATTERN is born. ARION now knows.
"""

import sqlite3
import json
import logging
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA STRUCTURES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class MemoryNode:
    id:            str
    type:          str        # event | emotion | person | topic | decision | insight
    content:       str
    person:        str
    timestamp:     str
    importance:    float      # 0.0 – 1.0
    access_count:  int        = 0
    last_accessed: str        = ""
    tags:          List[str]  = field(default_factory=list)
    decay_rate:    float      = 0.02  # importance drops by this per day unless accessed


@dataclass
class MemoryEdge:
    id:            str
    from_node:     str
    to_node:       str
    relation:      str        # CAUSED | FELT | SAID | LED_TO | RESOLVED_BY | CO_OCCURRED
    weight:        float      = 1.0
    created_at:    str        = ""


@dataclass
class CausalPattern:
    """A recurring cause → response → outcome cycle"""
    person:            str
    trigger_emotion:   str
    trigger_topic:     str
    successful_style:  str
    example_response:  str
    success_count:     int
    last_seen:         str


# ══════════════════════════════════════════════════════════════════════════════
#  CAUSAL MEMORY GRAPH
# ══════════════════════════════════════════════════════════════════════════════

class CausalMemoryGraph:
    """
    SQLite-backed causal memory.
    The Orchestrator calls this INLINE (no bus), so all methods are sync
    plus one async wrapper for the context query.
    """

    def __init__(self, db_path: str = "arion/data/causal_memory.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"[CausalMemoryGraph] Ready at {db_path}")

    # ── Schema ────────────────────────────────────────────────────────────────

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS exchanges (
                id               TEXT PRIMARY KEY,
                person           TEXT NOT NULL,
                user_message     TEXT NOT NULL,
                arion_reply      TEXT NOT NULL,
                emotion          TEXT DEFAULT 'neutral',
                emotion_intensity REAL DEFAULT 0.3,
                topic            TEXT DEFAULT 'general',
                implicit_outcome TEXT DEFAULT 'unknown',
                response_style   TEXT DEFAULT 'natural',
                timestamp        TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_ex_person ON exchanges(person);
            CREATE INDEX IF NOT EXISTS idx_ex_emotion ON exchanges(emotion);

            CREATE TABLE IF NOT EXISTS causal_nodes (
                id           TEXT PRIMARY KEY,
                type         TEXT NOT NULL,
                content      TEXT NOT NULL,
                person       TEXT NOT NULL,
                importance   REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                tags         TEXT DEFAULT '[]',
                decay_rate   REAL DEFAULT 0.02,
                timestamp    TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_cn_person ON causal_nodes(person);
            CREATE INDEX IF NOT EXISTS idx_cn_type   ON causal_nodes(type);

            CREATE TABLE IF NOT EXISTS causal_edges (
                id         TEXT PRIMARY KEY,
                from_node  TEXT NOT NULL,
                to_node    TEXT NOT NULL,
                relation   TEXT NOT NULL,
                weight     REAL DEFAULT 1.0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (from_node) REFERENCES causal_nodes(id),
                FOREIGN KEY (to_node)   REFERENCES causal_nodes(id)
            );
            CREATE INDEX IF NOT EXISTS idx_ce_from ON causal_edges(from_node);
            CREATE INDEX IF NOT EXISTS idx_ce_to   ON causal_edges(to_node);

            CREATE TABLE IF NOT EXISTS learned_patterns (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                person           TEXT NOT NULL,
                trigger_emotion  TEXT NOT NULL,
                trigger_topic    TEXT DEFAULT 'general',
                successful_style TEXT NOT NULL,
                example_response TEXT DEFAULT '',
                success_count    INTEGER DEFAULT 1,
                fail_count       INTEGER DEFAULT 0,
                last_seen        TEXT DEFAULT (datetime('now')),
                created_at       TEXT DEFAULT (datetime('now')),
                UNIQUE(person, trigger_emotion, trigger_topic, successful_style)
            );
            CREATE INDEX IF NOT EXISTS idx_lp_person ON learned_patterns(person, trigger_emotion);
        """)
        conn.commit()
        conn.close()

    # ── Write: record exchange ─────────────────────────────────────────────────

    def record_exchange(self, person: str, user_message: str,
                         arion_reply: str, emotion: str = "neutral",
                         emotion_intensity: float = 0.3,
                         topic: str = "general",
                         response_style: str = "natural") -> str:
        """
        Record every (user_message → arion_reply) pair in the graph.
        Returns the exchange_id.
        """
        import uuid
        exchange_id = f"ex_{int(datetime.now().timestamp()*1000)}_{uuid.uuid4().hex[:6]}"
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT OR IGNORE INTO exchanges
                (id, person, user_message, arion_reply, emotion,
                 emotion_intensity, topic, response_style)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (exchange_id, person, user_message[:500], arion_reply[:500],
                  emotion, emotion_intensity, topic, response_style))
            conn.commit()
        finally:
            conn.close()
        return exchange_id

    def update_exchange_outcome(self, person: str, outcome: str):
        """
        Called when the NEXT user message arrives.
        If emotion_intensity dropped → 'positive'.
        If intensified → 'negative'. Otherwise → 'neutral'.
        Updates the MOST RECENT exchange for this person.
        """
        if outcome not in ("positive", "negative", "neutral"):
            return
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                UPDATE exchanges SET implicit_outcome = ?
                WHERE person = ? AND implicit_outcome = 'unknown'
                AND id = (
                    SELECT id FROM exchanges WHERE person = ?
                    ORDER BY timestamp DESC LIMIT 1
                )
            """, (outcome, person, person))
            conn.commit()
        finally:
            conn.close()
        # If positive, bump the learned_pattern success count
        if outcome == "positive":
            self._promote_pattern(person)

    def store_event(self, person: str, event_type: str, content: str,
                    importance: float = 0.5, tags: List[str] = None) -> str:
        """Store a named event node in the graph."""
        import uuid
        node_id = f"node_{int(datetime.now().timestamp()*1000)}_{uuid.uuid4().hex[:6]}"
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT OR IGNORE INTO causal_nodes
                (id, type, content, person, importance, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (node_id, event_type, content[:400], person,
                  importance, json.dumps(tags or [])))
            conn.commit()
        finally:
            conn.close()
        return node_id

    def store_causal_link(self, from_id: str, to_id: str,
                           relation: str, weight: float = 1.0) -> str:
        """Link two graph nodes with a causal relationship."""
        import uuid
        edge_id = f"edge_{uuid.uuid4().hex[:10]}"
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT OR IGNORE INTO causal_edges (id, from_node, to_node, relation, weight)
                VALUES (?, ?, ?, ?, ?)
            """, (edge_id, from_id, to_id, relation, weight))
            conn.commit()
        finally:
            conn.close()
        return edge_id

    # ── Read: context for current message ─────────────────────────────────────

    def get_context_for_message(self, person: str,
                                 message: str,
                                 current_emotion: str = "neutral") -> str:
        """
        Given the current person + message + emotion,
        return a compact string of relevant causal context for the LLM prompt.
        Called synchronously from the Orchestrator pipeline.
        """
        context_parts: List[str] = []

        # 1. What worked before when this person had this emotion?
        pattern = self._best_pattern(person, current_emotion)
        if pattern:
            context_parts.append(
                f"[CAUSAL] When {self._firstname(person)} was {pattern.trigger_emotion} "
                f"about {pattern.trigger_topic}, a {pattern.successful_style} tone "
                f"worked {pattern.success_count} time{'s' if pattern.success_count > 1 else ''}."
            )

        # 2. Recent similar keywords in memory
        keyword_ctx = self._keyword_search(person, message)
        if keyword_ctx:
            context_parts.append(f"[PATTERN] {keyword_ctx}")

        # 3. High-importance unresolved events
        unresolved = self._unresolved_events(person)
        if unresolved:
            context_parts.append(f"[OPEN] {unresolved}")

        return "\n".join(context_parts) if context_parts else ""

    def get_pattern_insight(self, person: str) -> List[CausalPattern]:
        """Return all learned patterns for a person (for logging/debug)."""
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute("""
                SELECT trigger_emotion, trigger_topic, successful_style,
                       example_response, success_count, last_seen
                FROM learned_patterns
                WHERE person = ?
                ORDER BY success_count DESC
            """, (person,)).fetchall()
        finally:
            conn.close()
        return [CausalPattern(person=person, trigger_emotion=r[0],
                              trigger_topic=r[1], successful_style=r[2],
                              example_response=r[3], success_count=r[4],
                              last_seen=r[5])
                for r in rows]

    def query_by_emotion(self, person: str, emotion: str,
                          limit: int = 5) -> List[Dict]:
        """
        What past exchanges happened when this person was feeling X?
        Returns list of {user_message, arion_reply, outcome}.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute("""
                SELECT user_message, arion_reply, implicit_outcome, response_style
                FROM exchanges
                WHERE person = ? AND emotion = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (person, emotion, limit)).fetchall()
        finally:
            conn.close()
        return [{"user_message": r[0], "arion_reply": r[1],
                 "outcome": r[2], "style": r[3]}
                for r in rows]

    # ── Write: learn patterns automatically ───────────────────────────────────

    def _promote_pattern(self, person: str):
        """
        When an exchange outcome is marked positive, find the most recent
        exchange for this person and increment its pattern's success count.
        If pattern doesn't exist, create it.
        """
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute("""
                SELECT emotion, topic, response_style, arion_reply
                FROM exchanges WHERE person = ?
                ORDER BY timestamp DESC LIMIT 1
            """, (person,)).fetchone()
            if not row:
                return
            emotion, topic, style, reply = row
            short_reply = (reply or "")[:120]
            conn.execute("""
                INSERT INTO learned_patterns
                    (person, trigger_emotion, trigger_topic, successful_style, example_response)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(person, trigger_emotion, trigger_topic, successful_style)
                DO UPDATE SET success_count = success_count + 1,
                              last_seen = datetime('now'),
                              example_response = ?
            """, (person, emotion, topic or "general", style, short_reply, short_reply))
            conn.commit()
            logger.debug(f"[CausalGraph] Pattern promoted: {person} / {emotion} / {style}")
        finally:
            conn.close()

    def record_negative_outcome(self, person: str):
        """Increment fail count on the last pattern — reduces its score."""
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute("""
                SELECT emotion, topic, response_style FROM exchanges
                WHERE person = ? ORDER BY timestamp DESC LIMIT 1
            """, (person,)).fetchone()
            if row:
                conn.execute("""
                    UPDATE learned_patterns SET fail_count = fail_count + 1
                    WHERE person = ? AND trigger_emotion = ?
                    AND trigger_topic = ? AND successful_style = ?
                """, (person, row[0], row[1] or "general", row[2]))
                conn.commit()
        finally:
            conn.close()

    # ── Memory decay ──────────────────────────────────────────────────────────

    def decay_old_nodes(self) -> int:
        """
        Reduce importance of unaccessed nodes over time.
        Called by LearningScheduler. Returns number of nodes decayed.
        """
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            result = conn.execute("""
                UPDATE causal_nodes
                SET importance = MAX(0.0, importance - decay_rate)
                WHERE (last_accessed IS NULL OR last_accessed < ?)
                AND importance > 0.0
            """, (cutoff,))
            conn.commit()
            count = result.rowcount
            logger.info(f"[CausalGraph] Decayed {count} low-access nodes.")
            return count
        finally:
            conn.close()

    def prune_old_exchanges(self, keep_days: int = 90) -> int:
        """Remove exchanges older than keep_days (keeps learned_patterns intact)."""
        cutoff = (datetime.now() - timedelta(days=keep_days)).isoformat()
        conn = sqlite3.connect(self.db_path)
        try:
            result = conn.execute(
                "DELETE FROM exchanges WHERE timestamp < ?", (cutoff,))
            conn.commit()
            logger.info(f"[CausalGraph] Pruned {result.rowcount} old exchanges.")
            return result.rowcount
        finally:
            conn.close()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _best_pattern(self, person: str, emotion: str) -> Optional[CausalPattern]:
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute("""
                SELECT trigger_emotion, trigger_topic, successful_style,
                       example_response, success_count, last_seen
                FROM learned_patterns
                WHERE person = ? AND trigger_emotion = ?
                  AND success_count > fail_count
                ORDER BY (success_count - fail_count) DESC LIMIT 1
            """, (person, emotion)).fetchone()
        finally:
            conn.close()
        if not row:
            return None
        return CausalPattern(person=person, trigger_emotion=row[0],
                             trigger_topic=row[1], successful_style=row[2],
                             example_response=row[3], success_count=row[4],
                             last_seen=row[5])

    def _keyword_search(self, person: str, message: str,
                         limit: int = 2) -> str:
        """Find past exchanges mentioning the same keywords."""
        words = [w.lower() for w in message.split() if len(w) > 4][:5]
        if not words:
            return ""
        conn = sqlite3.connect(self.db_path)
        try:
            results = []
            for word in words:
                rows = conn.execute("""
                    SELECT user_message, implicit_outcome FROM exchanges
                    WHERE person = ? AND user_message LIKE ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (person, f"%{word}%")).fetchall()
                for r in rows:
                    if r[1] == "positive":
                        snippet = r[0][:60].strip()
                        results.append(f"similar past message resolved well: '{snippet}…'")
            return results[0] if results else ""
        finally:
            conn.close()

    def _unresolved_events(self, person: str) -> str:
        """Check for high-importance nodes that have no RESOLVED_BY edge."""
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute("""
                SELECT cn.content FROM causal_nodes cn
                WHERE cn.person = ? AND cn.importance >= 0.7
                  AND cn.type = 'event'
                  AND cn.id NOT IN (
                      SELECT from_node FROM causal_edges
                      WHERE relation = 'RESOLVED_BY'
                  )
                ORDER BY cn.timestamp DESC LIMIT 1
            """, (person,)).fetchall()
            if rows:
                return f"Ongoing open matter: {rows[0][0][:80]}"
            return ""
        finally:
            conn.close()

    @staticmethod
    def _firstname(jid_or_name: str) -> str:
        """Extract a readable first name from a JID or full name."""
        clean = jid_or_name.split("@")[0].split("_")[0]
        if clean.isdigit():
            return "them"
        return clean.split()[0].title()
