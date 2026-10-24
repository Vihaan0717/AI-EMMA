from typing import List, Optional
from core.hypothesis_models import Hypothesis
from core.cloud_reasoner import CloudReasoner
from core.code_analyzer import RepositoryAnalyzer

class HypothesisEngine:
    def __init__(self, reasoner: CloudReasoner, analyzer: RepositoryAnalyzer):
        self.reasoner = reasoner
        self.analyzer = analyzer

    def generate_and_rank(self, target_file: str, observation: str) -> Optional[Hypothesis]:
        """
        Analyzes a failure pattern or bottleneck and generates the best hypothesis.
        Strictly read-only process.
        """
        
        # 1. Fetch read-only architectural data
        try:
            blast_radius = self.analyzer.get_blast_radius(target_file)
            risk = self.analyzer.get_risk(target_file)
        except Exception as e:
            print(f"Failed to fetch architectural data for {target_file}: {e}")
            return None
            
        # 2. Immutable boundary check: Trust Anchors cannot be modified
        if risk.get("plane") == "CONTROL PLANE" and risk.get("risk") == "CRITICAL":
            print(f"REJECTED: {target_file} is a Control Plane Trust Anchor. Modifications are strictly forbidden.")
            return None
            
        # 3. Generate competing hypotheses
        hypotheses = self.reasoner.generate_hypotheses(observation, blast_radius, risk)
        if not hypotheses:
            return None
            
        # 4. Deterministic filtering and ranking
        # We want to maximize expected benefit (simulated by confidence for now, but ideally a separate metric),
        # minimize cost, and heavily penalize high blast radius or risk.
        
        def score_hypothesis(h: Hypothesis) -> float:
            # Base score from LLM confidence
            score = h.confidence * 100.0
            
            # Penalize by cost
            score -= (h.estimated_cost * 0.5)
            
            # Penalize by blast radius (more files affected = higher risk of regression)
            score -= (h.blast_radius * 1.5)
            
            # Risk multipliers
            risk_multiplier = {
                "CRITICAL": 0.1,  # Should rarely happen due to early rejection, but just in case
                "HIGH": 0.5,
                "MEDIUM": 0.8,
                "LOW": 1.0,
                "UNKNOWN": 0.5
            }
            score *= risk_multiplier.get(h.risk, 0.5)
            
            return score
            
        # Sort descending by score
        ranked = sorted(hypotheses, key=score_hypothesis, reverse=True)
        
        if not ranked:
            return None
            
        best_candidate = ranked[0]
        print(f"Selected Hypothesis {best_candidate.hypothesis_id} with score {score_hypothesis(best_candidate):.2f}")
        return best_candidate
