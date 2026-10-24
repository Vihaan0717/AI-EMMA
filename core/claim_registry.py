import uuid
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def generate_uuid() -> str:
    return str(uuid.uuid4())

def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

class Claim(BaseModel):
    claim_id: str = Field(default_factory=generate_uuid)
    agent: str
    content: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)
    challenging_messages: List[str] = Field(default_factory=list)
    
    # New fields for provenance and status decoupling
    created_by_message_id: Optional[str] = None
    last_updated_by_message_id: Optional[str] = None
    claim_type: str = "fact" # "fact", "opinion", "prediction"
    verification_status: str = "UNVERIFIED" # UNVERIFIED, SUPPORTED, CHALLENGED, CORRECTED, VERIFIED, REJECTED
    
    created_at: str = Field(default_factory=current_iso_timestamp)
    updated_at: str = Field(default_factory=current_iso_timestamp)

class ClaimRegistry:
    def __init__(self):
        self._claims = {}

    def register_claim(self, claim: Claim) -> str:
        self._claims[claim.claim_id] = claim
        return claim.claim_id

    def get_claim(self, claim_id: str) -> Optional[Claim]:
        return self._claims.get(claim_id)
        
    def add_supporting_evidence(self, claim_id: str, evidence_id: str, message_id: str = None):
        if claim_id in self._claims:
            self._claims[claim_id].supporting_evidence.append(evidence_id)
            if message_id:
                self._claims[claim_id].last_updated_by_message_id = message_id
            self._claims[claim_id].updated_at = current_iso_timestamp()

    def add_challenging_message(self, claim_id: str, message_id: str):
        if claim_id in self._claims:
            self._claims[claim_id].challenging_messages.append(message_id)
            self._claims[claim_id].verification_status = "CHALLENGED"
            self._claims[claim_id].last_updated_by_message_id = message_id
            self._claims[claim_id].updated_at = current_iso_timestamp()

    def update_verification_status(self, claim_id: str, status: str, message_id: str = None):
        if claim_id in self._claims:
            self._claims[claim_id].verification_status = status
            if message_id:
                self._claims[claim_id].last_updated_by_message_id = message_id
            self._claims[claim_id].updated_at = current_iso_timestamp()

    def list_claims_by_status(self, status: str) -> List[Claim]:
        return [c for c in self._claims.values() if c.verification_status == status]

    def all_claims(self) -> List[Claim]:
        return list(self._claims.values())
