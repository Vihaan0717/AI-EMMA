import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from core.database import db_manager
from core.logger import get_logger

logger = get_logger("DataLayer")


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


@dataclass
class InteractionRecord:
    channel: str
    user_input: str
    response: str
    outcome: str = "responded"
    metadata: dict[str, Any] | None = None


class SQLiteStore:
    """Small SQLite wrapper for backend-only persistence."""

    def __init__(self, db_path: str = "memory/jarvis_core.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS interaction_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel TEXT NOT NULL,
                user_input TEXT NOT NULL,
                response TEXT NOT NULL,
                outcome TEXT NOT NULL,
                metadata_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER,
                feedback_type TEXT NOT NULL,
                score REAL,
                note TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(scope, key)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                due_at TEXT,
                source TEXT NOT NULL,
                details_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()


class FeedbackRepository:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def log_interaction(self, record: InteractionRecord) -> int:
        conn = self.store._connect()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO interaction_log (channel, user_input, response, outcome, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record.channel,
                record.user_input,
                record.response,
                record.outcome,
                json.dumps(record.metadata or {}),
                _utc_now(),
            ),
        )
        row_id = cur.lastrowid
        conn.commit()
        conn.close()
        return row_id


class PreferenceRepository:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def set(self, key: str, value: str, scope: str = "global"):
        conn = self.store._connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO preferences (scope, key, value, updated_at) VALUES (?, ?, ?, ?)",
            (scope, key, value, _utc_now()),
        )
        conn.commit()
        conn.close()

    def get(self, key: str, scope: str = "global", default: Any = None) -> Any:
        conn = self.store._connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT value FROM preferences WHERE scope = ? AND key = ?", (scope, key)
        )
        row = cur.fetchone()
        conn.close()
        return row["value"] if row else default


class TaskRepository:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def add(
        self,
        title: str,
        details: dict = None,
        source: str = "user",
        due_at: str = None,
    ):
        conn = self.store._connect()
        cur = conn.cursor()
        now = _utc_now()
        cur.execute(
            """
            INSERT INTO tasks (title, status, due_at, source, details_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                "pending",
                due_at,
                source,
                json.dumps(details or {}),
                now,
                now,
            ),
        )
        conn.commit()
        conn.close()

    def list_pending(self, limit: int = 5) -> list:
        """Return pending tasks. Used by ContextAssembler."""
        try:
            conn = self.store._connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT title, status, due_at FROM tasks WHERE status = 'pending' ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cur.fetchall()
            conn.close()
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.warning(f"Failed to list pending tasks: {e}")
            return []

class CloudStore:
    """Wrapper that routes data to Supabase with local SQLite fallback."""
    def __init__(self, db_path: str = "memory/jarvis_core.db"):
        self.local = SQLiteStore(db_path=db_path)
        self.cloud = db_manager

    def log_interaction(self, record: InteractionRecord) -> int | None:
        # 1. Store in Cloud
        try:
            payload = {
                "channel": record.channel,
                "user_input": record.user_input,
                "response": record.response,
                "outcome": record.outcome,
                "metadata_json": record.metadata or {},
                "created_at": _utc_now()
            }
            res = self.cloud.log_interaction(payload)
            if res: return res.data[0].get("id")
        except Exception as e:
            logger.warning(f"Cloud log failed, falling back to local: {e}")
        
        # 2. Fallback to Local
        repo = FeedbackRepository(self.local)
        return repo.log_interaction(record)

    def set_preference(self, key: str, value: str, scope: str = "global"):
        try:
            self.cloud.upsert_setting(key, value, scope)
        except:
            pass
        repo = PreferenceRepository(self.local)
        repo.set(key, value, scope)

    def get_preference(self, key: str, scope: str = "global", default: str = ""):
        # For simple get, we check local first then cloud if missing? 
        # Or always cloud for 'global' sentient state?
        repo = PreferenceRepository(self.local)
        val = repo.get(key, scope, None)
        if val is None and self.cloud.supabase:
            try:
                res = self.cloud.supabase.table("settings").select("value").eq("key", key).eq("scope", scope).execute()
                if res.data: return res.data[0]["value"]
            except:
                pass
        return val or default

    def set(self, key: str, value: str, scope: str = "global"):
        """Alias for backward compatibility."""
        return self.set_preference(key, value, scope)

    def get(self, key: str, scope: str = "global", default: Any = None) -> Any:
        """Alias for backward compatibility."""
        return self.get_preference(key, scope, default)

    def list(self) -> dict:
        """Return all preferences as a dict. Used by ContextAssembler."""
        try:
            repo = PreferenceRepository(self.local)
            conn = repo.store._connect()
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM preferences")
            rows = cur.fetchall()
            conn.close()
            return {row["key"]: row["value"] for row in rows} if rows else {}
        except Exception as e:
            logger.warning(f"Failed to list preferences: {e}")
            return {}

    def recent_interactions(self, limit: int = 3) -> list:
        """Return recent interactions. Used by ContextAssembler."""
        try:
            conn = self.local._connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT user_input, response, outcome FROM interaction_log ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cur.fetchall()
            conn.close()
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.warning(f"Failed to get recent interactions: {e}")
            return []

class TaskRepository:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def add(
        self,
        title: str,
        details: dict = None,
        source: str = "user",
        due_at: str = None,
    ):
        conn = self.store._connect()
        cur = conn.cursor()
        now = _utc_now()
        cur.execute(
            """
            INSERT INTO tasks (title, status, due_at, source, details_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                "pending",
                due_at,
                source,
                json.dumps(details or {}),
                now,
                now,
            ),
        )
        conn.commit()
        conn.close()

    def list_pending(self, limit: int = 5) -> list:
        """Return pending tasks. Used by ContextAssembler."""
        try:
            conn = self.store._connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT title, status, due_at FROM tasks WHERE status = 'pending' ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cur.fetchall()
            conn.close()
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.warning(f"Failed to list pending tasks: {e}")
            return []

class JarvisDataLayer:
    """Single backend entry point for structured storage (Cloud Optimized)."""

    def __init__(self, db_path: str = "memory/jarvis_core.db"):
        self.store = CloudStore(db_path=db_path)
        self.feedback = self.store
        self.preferences = self.store
        # Task repo still uses local for now until complex migration
        self.tasks = TaskRepository(self.store.local)


data_layer = JarvisDataLayer()
