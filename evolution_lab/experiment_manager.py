import sqlite3
import os
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from evolution_lab.reasoner import CloudReasoner, ReasonerPayload
from evolution_lab.failure_analyzer import FailurePattern
from core.system_limits import LimitEnforcer, ExperimentLimits, LimitExceededException

def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

class ExperimentFingerprint(BaseModel):
    experiment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dataset_version: str = "v1"
    benchmark_version: str = "v1"
    prompt_version: str = "unknown"
    router_version: str = "unknown"
    retrieval_version: str = "unknown"
    model: str
    timestamp: str = Field(default_factory=current_iso_timestamp)

class CandidateConfiguration(BaseModel):
    candidate_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    experiment_id: str
    config_data: Dict[str, Any]
    status: str = "PENDING" # PENDING, TESTED, REJECTED, PROMOTED

class ExperimentManager:
    def __init__(self, db_path: str = "logs/evolution.db", reasoner: Optional[CloudReasoner] = None):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.reasoner = reasoner
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id TEXT PRIMARY KEY,
                fingerprint_json TEXT,
                pattern_id TEXT,
                created_at TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_id TEXT PRIMARY KEY,
                experiment_id TEXT,
                config_json TEXT,
                status TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def generate_experiment(self, pattern: FailurePattern, current_versions: Dict[str, str]) -> List[CandidateConfiguration]:
        """
        Takes a validated failure pattern and uses the CloudReasoner to propose an Experiment
        with multiple Candidates.
        """
        if not self.reasoner:
            raise ValueError("Reasoner not configured.")
            
        # 1. Enforce limits on experiment creation
        # Using a mock API budget check for demonstration
        api_budget_remaining = 50.0
        if api_budget_remaining < ExperimentLimits.MAX_API_BUDGET_USD:
             raise LimitExceededException("EXPERIMENT LIMIT REACHED: API Budget")

        # 2. Get proposals from Reasoner
        payloads: List[ReasonerPayload] = self.reasoner.generate_hypothesis(pattern.model_dump())
        
        # Limit candidates
        payloads = payloads[:ExperimentLimits.MAX_CANDIDATES_PER_EXP]
        
        # 3. Create Fingerprint
        fingerprint = ExperimentFingerprint(
            model=payloads[0].model if payloads else "unknown",
            prompt_version=current_versions.get("prompt", "unknown"),
            router_version=current_versions.get("router", "unknown"),
            retrieval_version=current_versions.get("retrieval", "unknown")
        )
        
        # 4. Save Experiment
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO experiments (experiment_id, fingerprint_json, pattern_id, created_at)
            VALUES (?, ?, ?, ?)
        ''', (fingerprint.experiment_id, fingerprint.model_dump_json(), pattern.pattern_id, fingerprint.timestamp))
        
        # 5. Save Candidates
        candidates = []
        for payload in payloads:
            cand = CandidateConfiguration(
                experiment_id=fingerprint.experiment_id,
                config_data=payload.proposal,
                status="PENDING"
            )
            candidates.append(cand)
            c.execute('''
                INSERT INTO candidates (candidate_id, experiment_id, config_json, status)
                VALUES (?, ?, ?, ?)
            ''', (cand.candidate_id, cand.experiment_id, json.dumps(cand.config_data), cand.status))
            
        conn.commit()
        conn.close()
        return candidates

    def update_candidate_status(self, candidate_id: str, status: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE candidates SET status = ? WHERE candidate_id = ?', (status, candidate_id))
        conn.commit()
        conn.close()
