from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time

class Provenance(BaseModel):
    source: str
    timestamp: float = Field(default_factory=time.time)
    confidence: float

class MetacognitiveVariable(BaseModel):
    value: Any
    provenance: Provenance

class OperationalState(BaseModel):
    """
    Deterministic state object representing JARVIS's actual machine state.
    The LLM reads this, but cannot invent it.
    """
    capability_state: Dict[str, MetacognitiveVariable] = Field(default_factory=dict)
    resource_state: Dict[str, MetacognitiveVariable] = Field(default_factory=dict)
    knowledge_state: Dict[str, MetacognitiveVariable] = Field(default_factory=dict)
    uncertainty_state: Dict[str, MetacognitiveVariable] = Field(default_factory=dict)
    contradiction_state: Dict[str, MetacognitiveVariable] = Field(default_factory=dict)
    goal_state: Dict[str, MetacognitiveVariable] = Field(default_factory=dict)
    safety_state: Dict[str, MetacognitiveVariable] = Field(default_factory=dict)
    dependency_state: Dict[str, MetacognitiveVariable] = Field(default_factory=dict)
