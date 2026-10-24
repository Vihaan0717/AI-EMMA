import os
import time
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ReasonerPayload(BaseModel):
    proposal: Dict[str, Any]
    reasoning_metadata: Dict[str, Any]
    model: str
    cost: float
    timestamp: float = Field(default_factory=time.time)

class CloudReasoner:
    """Base unified interface for cloud reasoning generation."""
    def generate_hypothesis(self, failure_pattern: Dict[str, Any]) -> List[ReasonerPayload]:
        raise NotImplementedError

class MockReasoner(CloudReasoner):
    """Deterministic mock reasoner for sandbox tests."""
    def generate_hypothesis(self, failure_pattern: Dict[str, Any]) -> List[ReasonerPayload]:
        # Based on the failure pattern (e.g. retrieval fails on long queries)
        # the MockReasoner generates some deterministic config variations.
        
        candidates = []
        if failure_pattern.get("failure_type") == "retrieval":
            candidates = [
                {"retrieval": {"top_k": 8, "chunk_size": 1200}},
                {"retrieval": {"top_k": 8, "chunk_size": 900}},
                {"retrieval": {"top_k": 8, "chunk_size": 600}}
            ]
        elif failure_pattern.get("failure_type") == "routing":
            candidates = [
                {"routing": {"coding": "cloud_reasoner", "simple_question": "local"}},
                {"routing": {"coding": "local", "simple_question": "local"}}
            ]
            
        payloads = []
        for c in candidates:
            payloads.append(
                ReasonerPayload(
                    proposal=c,
                    reasoning_metadata={"confidence": 0.9, "rationale": "mock rationale"},
                    model="MockReasoner-v1",
                    cost=0.0
                )
            )
        return payloads

# Future implementations could include GeminiReasoner, etc.
