import uuid
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class CollaborationSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    topic: str
    participants: List[str]
    current_round: int = 1
    max_rounds: int = 3
    message_count: int = 0
    max_messages: int = 20
    max_llm_calls: int = 10
    max_total_tokens: int = 10000
    max_duration_seconds: int = 120
    status: str = "active"  # active, closed
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ended_at: Optional[str] = None
    outcome: Optional[str] = None  # CONSENSUS, PARTIAL_CONSENSUS, DISAGREEMENT, VERIFICATION_FAILED, TIMEOUT, ERROR

    def end_session(self, outcome: str):
        self.status = "closed"
        self.outcome = outcome
        self.ended_at = datetime.now(timezone.utc).isoformat()
