from typing import List, Dict, Any
import uuid
from core.hypothesis_models import Hypothesis

class CloudReasoner:
    """Base interface for the cloud reasoner (LLM)."""
    def generate_hypotheses(self, observation: str, blast_radius_data: Dict[str, Any], risk_data: Dict[str, str]) -> List[Hypothesis]:
        raise NotImplementedError

class MockReasoner(CloudReasoner):
    """
    Simulates an LLM generating multiple candidate hypotheses.
    In tests, we provide a deterministic bottleneck or failure pattern.
    """
    def __init__(self, target_file: str):
        self.target_file = target_file

    def generate_hypotheses(self, observation: str, blast_radius_data: Dict[str, Any], risk_data: Dict[str, str]) -> List[Hypothesis]:
        """
        Generates a few competing hypotheses based on the observation.
        """
        num_dependents = len(blast_radius_data.get("direct_dependents", [])) + len(blast_radius_data.get("indirect_dependents", []))
        plane = risk_data.get("plane", "UNKNOWN")
        risk = risk_data.get("risk", "UNKNOWN")
        
        # Hypothesis 1: Naive/high confidence but maybe high risk
        h1 = Hypothesis(
            goal_id="GOAL-31",
            failure_id="FAIL-882",
            hypothesis_id=str(uuid.uuid4())[:8],
            target=self.target_file,
            observation=observation,
            proposed_change="Rewrite the entire module to be async.",
            expected_benefit="Massive concurrent throughput increase.",
            confidence=0.9,
            risk=risk,
            blast_radius=num_dependents,
            required_tests=["Level 8 regression", "Level 8.5 reliability"],
            estimated_cost=100.0,
            evidence="Async IO is generally faster for I/O bound tasks."
        )
        
        # Hypothesis 2: Targeted caching (usually a good idea)
        h2 = Hypothesis(
            goal_id="GOAL-31",
            failure_id="FAIL-882",
            hypothesis_id=str(uuid.uuid4())[:8],
            target=self.target_file,
            observation=observation,
            proposed_change="Cache dependency readiness for unchanged task graphs.",
            expected_benefit="Reduced scheduling overhead.",
            confidence=0.85,
            risk=risk,
            blast_radius=num_dependents,
            required_tests=["Level 8 regression", "Level 8.5 reliability", "endurance test"],
            estimated_cost=20.0,
            evidence="Repeated dependency checks account for high CPU overhead."
        )
        
        # Hypothesis 3: Micro-optimization
        h3 = Hypothesis(
            goal_id="GOAL-31",
            failure_id="FAIL-882",
            hypothesis_id=str(uuid.uuid4())[:8],
            target=self.target_file,
            observation=observation,
            proposed_change="Use tuples instead of lists for internal state representation.",
            expected_benefit="Slight memory reduction.",
            confidence=0.6,
            risk=risk,
            blast_radius=num_dependents,
            required_tests=["Level 8 regression"],
            estimated_cost=5.0,
            evidence="Tuples are more memory efficient."
        )
        
        return [h1, h2, h3]
