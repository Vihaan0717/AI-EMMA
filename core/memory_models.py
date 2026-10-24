import uuid
from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def generate_uuid() -> str:
    return str(uuid.uuid4())

def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

class MemoryStatus(str, Enum):
    NEW = "NEW"
    UNVERIFIED = "UNVERIFIED"
    OBSERVED = "OBSERVED"
    SUPPORTED = "SUPPORTED"
    CHALLENGED = "CHALLENGED"
    VERIFIED = "VERIFIED"
    ESTABLISHED = "ESTABLISHED"
    CONTRADICTED = "CONTRADICTED"
    REJECTED = "REJECTED"
    STALE = "STALE"
    SUPERSEDED = "SUPERSEDED"

class MemoryType(str, Enum):
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    PROCEDURAL = "PROCEDURAL"

class MemoryStability(str, Enum):
    TEMPORAL = "TEMPORAL"
    SEMI_STABLE = "SEMI_STABLE"
    STABLE = "STABLE"

class MemoryAccess(str, Enum):
    PRIVATE = "PRIVATE"
    AGENT_SHARED = "AGENT_SHARED"
    GLOBAL_VERIFIED = "GLOBAL_VERIFIED"

class MemoryProvenance(BaseModel):
    experience_id: str
    session_id: str
    message_ids: List[str] = Field(default_factory=list)
    claim_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)

class MemoryItem(BaseModel):
    memory_id: str = Field(default_factory=generate_uuid)
    memory_type: MemoryType
    access_level: MemoryAccess
    
    agent_id: Optional[str] = None
    
    # Core content
    content: str
    claim: Optional[str] = None
    
    # Status and confidence
    status: MemoryStatus = MemoryStatus.UNVERIFIED
    verified: bool = False
    
    # Statistical confidence (not just a naive float)
    independent_sources: int = 0
    sources_count: int = 0
    successful_verifications: int = 0
    contradictions: int = 0
    
    confidence: float = 0.0
    freshness: float = 1.0
    agreement: float = 0.0
    
    stability: MemoryStability = MemoryStability.TEMPORAL
    
    provenance: MemoryProvenance
    
    created_at: str = Field(default_factory=current_iso_timestamp)
    last_verified: str = Field(default_factory=current_iso_timestamp)
    
    def calculate_stability_score(self) -> float:
        """
        Calculates stability using evidence quality, temporal characteristics, domain, and contradiction history.
        """
        base_score = (self.successful_verifications * 10) + (self.independent_sources * 5)
        penalty = self.contradictions * 15
        
        # In a real system, age in days would impact the score depending on `self.stability`
        age_bonus = 0 if self.stability == MemoryStability.TEMPORAL else 5
        
        score = base_score - penalty + age_bonus
        return float(max(0, score))
    
    def resolve_conflict(self, new_memory: "MemoryItem") -> "MemoryItem":
        """
        Handles memory conflict resolution by superseding this memory
        if the new one is verified.
        """
        if new_memory.status in [MemoryStatus.VERIFIED, MemoryStatus.ESTABLISHED]:
            self.status = MemoryStatus.SUPERSEDED
        return new_memory
