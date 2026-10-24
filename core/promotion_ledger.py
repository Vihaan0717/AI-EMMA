import json
import sqlite3
import os
import datetime
import uuid
from typing import Dict, Any, List

class PromotionLedger:
    """
    Immutable ledger of all candidate promotions and demotions (rollbacks).
    Records the full evolutionary chain.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        dirname = os.path.dirname(self.db_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS promotions (
                    promotion_id TEXT PRIMARY KEY,
                    candidate_id TEXT,
                    hypothesis_id TEXT,
                    parent_version TEXT,
                    benchmark_hash TEXT,
                    sample_count INTEGER,
                    champion_score REAL,
                    challenger_score REAL,
                    resource_metrics TEXT,
                    security_result TEXT,
                    decision TEXT,
                    decision_reason TEXT,
                    timestamp TEXT,
                    rollback_status TEXT
                )
            ''')
            
    def record_decision(self, record: Dict[str, Any]):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO promotions (
                    promotion_id, candidate_id, hypothesis_id, parent_version,
                    benchmark_hash, sample_count, champion_score, challenger_score,
                    resource_metrics, security_result, decision, decision_reason,
                    timestamp, rollback_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get("promotion_id", f"PROM-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"),
                record.get("candidate_id", ""),
                record.get("hypothesis_id", ""),
                record.get("parent_version", ""),
                record.get("benchmark_hash", ""),
                record.get("sample_count", 0),
                record.get("champion_score", 0.0),
                record.get("challenger_score", 0.0),
                json.dumps(record.get("resource_metrics", {})),
                record.get("security_result", "PASS"),
                record.get("decision", "REJECTED"),
                record.get("decision_reason", ""),
                datetime.datetime.now(datetime.timezone.utc).isoformat(),
                record.get("rollback_status", "NONE")
            ))
            conn.commit()
            
    def mark_rollback(self, candidate_id: str, reason: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                UPDATE promotions 
                SET rollback_status = ? 
                WHERE candidate_id = ? AND decision = 'APPROVED'
            ''', (f"ROLLED_BACK: {reason}", candidate_id))
            print(f"DEBUG mark_rollback for {candidate_id}, rows updated: {cursor.rowcount}")
            conn.commit()
            
    def get_history(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM promotions ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]
