from enum import Enum
import uuid
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

def generate_uuid() -> str:
    return str(uuid.uuid4())

class GoalHealth(str, Enum):
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    RUNNING = "RUNNING"
    VERIFYING = "VERIFYING"
    HEALTHY = "HEALTHY"
    AT_RISK = "AT_RISK"
    BLOCKED = "BLOCKED"
    STALE = "STALE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    INTERRUPTED = "INTERRUPTED"

class AutonomyBudget(BaseModel):
    max_runtime_seconds: int
    max_tasks: int
    max_retries: int
    max_api_calls: int
    max_tokens: int
    max_storage_mb: int
    max_concurrent_workers: int
    max_cost_usd: float
    max_autonomy_depth: int
    allowed_tools: List[str]
    allowed_domains: List[str]

class CompletionCriteria(BaseModel):
    conditions: List[str]
    required_confidence: float = 0.9

class Evidence(BaseModel):
    verified: bool = False
    details: str = ""
    metrics: Dict[str, float] = Field(default_factory=dict)

class GoalMetrics(BaseModel):
    importance: float = 1.0     # 0.0 to 10.0
    urgency: float = 1.0        # 0.0 to 10.0
    dependency_value: float = 1.0 # Extra weight if blocking other tasks
    expected_benefit: float = 1.0
    confidence: float = 1.0
    estimated_cost: float = 1.0 # time/API cost (must be > 0)
    
    def calculate_priority(self, resource_availability: float = 1.0, dependency_readiness: float = 1.0) -> float:
        """Priority = ((importance * urgency * dependency_value * expected_benefit * confidence) / estimated_cost) * resource_availability * dependency_readiness"""
        num = self.importance * self.urgency * self.dependency_value * self.expected_benefit * self.confidence
        base_priority = num / max(0.1, self.estimated_cost)
        return base_priority * resource_availability * dependency_readiness

class Task(BaseModel):
    task_id: str = Field(default_factory=generate_uuid)
    goal_id: str
    description: str
    status: GoalHealth = GoalHealth.PENDING
    metrics: GoalMetrics = Field(default_factory=GoalMetrics)
    dependencies: List[str] = Field(default_factory=list) # List of task_ids
    progress: float = 0.0 # 0.0 to 1.0
    
    # Execution Tracking
    worker_id: Optional[str] = None
    last_heartbeat: float = Field(default_factory=time.time)
    idempotency_key: Optional[str] = None
    
    # Verification
    completion_criteria: Optional[CompletionCriteria] = None
    evidence: Optional[Evidence] = None
    
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    def generate_idempotency_key(self, operation_id: str):
        self.idempotency_key = f"{self.goal_id}:{self.task_id}:{operation_id}"

class Goal(BaseModel):
    goal_id: str = Field(default_factory=generate_uuid)
    parent_goal_id: Optional[str] = None
    description: str
    status: GoalHealth = GoalHealth.HEALTHY
    progress: float = 0.0
    budget: AutonomyBudget
    completion_criteria: Optional[CompletionCriteria] = None
    evidence: Optional[Evidence] = None
    tasks: List[Task] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
