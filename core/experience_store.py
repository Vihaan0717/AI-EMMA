import sqlite3
import json
import uuid
import os
from typing import Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def generate_uuid() -> str:
    return str(uuid.uuid4())

class ExperienceRecord(BaseModel):
    experience_id: str = Field(default_factory=generate_uuid)
    session_id: str
    agent: str
    topic: str
    input: str
    action: str
    output: str
    outcome: str = "success"
    claims_json: str = "[]"
    evidence_json: str = "[]"
    errors_json: str = "[]"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ExperienceStore:
    def __init__(self, db_path: str = "logs/experience_log.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS experiences (
                experience_id TEXT PRIMARY KEY,
                session_id TEXT,
                agent TEXT,
                topic TEXT,
                input TEXT,
                action TEXT,
                output TEXT,
                outcome TEXT,
                claims_json TEXT,
                evidence_json TEXT,
                errors_json TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def append_experience(self, exp: ExperienceRecord) -> str:
        """
        Append-only operation. We do not allow UPDATE or DELETE.
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO experiences (
                experience_id, session_id, agent, topic, input, action, 
                output, outcome, claims_json, evidence_json, errors_json, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            exp.experience_id, exp.session_id, exp.agent, exp.topic, exp.input, exp.action,
            exp.output, exp.outcome, exp.claims_json, exp.evidence_json, exp.errors_json, exp.timestamp
        ))
        conn.commit()
        conn.close()
        return exp.experience_id
        
    def get_experiences_by_session(self, session_id: str) -> List[ExperienceRecord]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM experiences WHERE session_id = ? ORDER BY timestamp ASC', (session_id,))
        rows = c.fetchall()
        conn.close()
        
        experiences = []
        for r in rows:
            experiences.append(ExperienceRecord(
                experience_id=r[0],
                session_id=r[1],
                agent=r[2],
                topic=r[3],
                input=r[4],
                action=r[5],
                output=r[6],
                outcome=r[7],
                claims_json=r[8],
                evidence_json=r[9],
                errors_json=r[10],
                timestamp=r[11]
            ))
        return experiences
