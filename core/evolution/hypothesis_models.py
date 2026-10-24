from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Hypothesis:
    goal_id: str
    failure_id: str
    hypothesis_id: str
    target: str
    observation: str
    proposed_change: str
    expected_benefit: str
    confidence: float # 0.0 to 1.0
    risk: str # CRITICAL, HIGH, MEDIUM, LOW
    blast_radius: int # Number of affected files
    required_tests: List[str]
    estimated_cost: float # Arbitrary cost unit (e.g. implementation time or computational cost)
    evidence: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "failure_id": self.failure_id,
            "hypothesis_id": self.hypothesis_id,
            "target": self.target,
            "observation": self.observation,
            "proposed_change": self.proposed_change,
            "expected_benefit": self.expected_benefit,
            "confidence": self.confidence,
            "risk": self.risk,
            "blast_radius": self.blast_radius,
            "required_tests": self.required_tests,
            "estimated_cost": self.estimated_cost,
            "evidence": self.evidence
        }
