import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Strict enumerations for message_type
ALLOWED_MESSAGE_TYPES = {
    "QUESTION", "ANSWER", "RESEARCH_FINDING", "EVIDENCE", 
    "CHALLENGE", "CORRECTION", "AGREEMENT", "DISAGREEMENT", 
    "VERIFICATION_REQUEST", "VERIFICATION_RESULT", "HELP_REQUEST", 
    "HELP_RESPONSE", "PREDICTION", "HYPOTHESIS", "TASK_PROPOSAL", 
    "TASK_RESULT", "KNOWLEDGE_UPDATE"
}

def generate_uuid() -> str:
    return str(uuid.uuid4())

def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

class AgentMessage(BaseModel):
    message_id: str = Field(default_factory=generate_uuid)
    conversation_id: str
    sender: str
    recipient: str
    message_type: str
    topic: str = ""
    content: str = ""
    evidence: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    requires_response: bool = False
    parent_message_id: Optional[str] = None
    claim_id: Optional[str] = None
    round_id: int = 1
    priority: str = "normal"  # "low", "normal", "high", "critical"
    status: str = "pending"   # "pending", "delivered", "acknowledged", "responded", "failed", "expired"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=current_iso_timestamp)
    
    # Custom validator to strictly enforce message_type
    def validate_message_type(self):
        if self.message_type not in ALLOWED_MESSAGE_TYPES:
            raise ValueError(f"Invalid message_type '{self.message_type}'. Allowed types: {ALLOWED_MESSAGE_TYPES}")
        if self.priority not in ["low", "normal", "high", "critical"]:
            raise ValueError(f"Invalid priority '{self.priority}'")
        if self.status not in ["pending", "delivered", "acknowledged", "responded", "failed", "expired"]:
            raise ValueError(f"Invalid status '{self.status}'")

    def __init__(self, **data):
        super().__init__(**data)
        self.validate_message_type()
