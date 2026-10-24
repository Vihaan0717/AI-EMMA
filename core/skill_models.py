import uuid
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def generate_uuid() -> str:
    return str(uuid.uuid4())

def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

class SkillStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    ESTABLISHED = "ESTABLISHED"
    DEPRECATED = "DEPRECATED"
    REJECTED = "REJECTED"

class CapabilityAction(BaseModel):
    action: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class Skill(BaseModel):
    skill_id: str = Field(default_factory=generate_uuid)
    skill_name: str
    agent: str
    domain: str
    version: int = 1
    status: SkillStatus = SkillStatus.CANDIDATE
    
    # Procedure is a list of deterministic CapabilityActions, NEVER arbitrary LLM strings
    procedure: List[CapabilityAction]
    
    # Exhaustive Metrics (Not LLM personality claims)
    attempts: int = 0
    successful_outcomes: int = 0
    failed_outcomes: int = 0
    verified_outcomes: int = 0
    challenged_outcomes: int = 0
    regressions: int = 0
    benchmark_score: float = 0.0
    
    created_at: str = Field(default_factory=current_iso_timestamp)
    last_used: Optional[str] = None
    last_verified: Optional[str] = None

class ExpertiseProfile(BaseModel):
    agent_id: str
    domain_scores: Dict[str, float] = Field(default_factory=dict) # e.g. {"Research": 0.94}
    tasks_evaluated: int = 0
    verified_outcomes: int = 0
    failures: int = 0
    regressions: int = 0
    established_skills: int = 0
    
    def update_metrics(self, domain: str, success: bool, verified: bool = False, regression: bool = False):
        self.tasks_evaluated += 1
        if success:
            # We don't track successful_outcomes explicitly in the profile in the user's example, 
            # but domain_scores requires it. We'll simplify.
            pass
        else:
            self.failures += 1
            
        if verified:
            self.verified_outcomes += 1
            
        if regression:
            self.regressions += 1
            
        # Recompute domain score (dummy logic for now)
        current = self.domain_scores.get(domain, 0.80)
        if success:
            self.domain_scores[domain] = min(1.0, current + 0.01)
        else:
            self.domain_scores[domain] = max(0.0, current - 0.05)
