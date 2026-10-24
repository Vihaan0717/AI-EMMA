import uuid
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def generate_uuid() -> str:
    return str(uuid.uuid4())

def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

class Evidence(BaseModel):
    evidence_id: str = Field(default_factory=generate_uuid)
    source: str
    source_type: str # e.g. "web_search", "document", "vault_memory"
    claim_ids: List[str] = Field(default_factory=list)
    reliability: float = Field(default=0.5, ge=0.0, le=1.0)
    verification_status: str = "UNVERIFIED" # UNVERIFIED, VERIFIED, DISPROVEN
    
    # Provenance
    created_by_message_id: Optional[str] = None
    conversation_id: Optional[str] = None # To prevent cross-session contamination
    
    timestamp: str = Field(default_factory=current_iso_timestamp)

class EvidenceRegistry:
    def __init__(self):
        self._evidence = {}

    def register_evidence(self, evidence: Evidence) -> str:
        self._evidence[evidence.evidence_id] = evidence
        return evidence.evidence_id

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        return self._evidence.get(evidence_id)
        
    def link_to_claim(self, evidence_id: str, claim_id: str):
        if evidence_id in self._evidence:
            if claim_id not in self._evidence[evidence_id].claim_ids:
                self._evidence[evidence_id].claim_ids.append(claim_id)

    def update_verification_status(self, evidence_id: str, status: str, reliability: Optional[float] = None):
        if evidence_id in self._evidence:
            self._evidence[evidence_id].verification_status = status
            if reliability is not None:
                self._evidence[evidence_id].reliability = reliability

    def all_evidence(self) -> List[Evidence]:
        return list(self._evidence.values())
