import os
import logging
from typing import Dict, Any, List

from core.candidate_models import CandidateManifest
from core.validation_models import ValidationScorecard
from core.promotion_ledger import PromotionLedger

logger = logging.getLogger("jarvis.promotion_gate")

TRUST_ANCHORS = [
    "core/system_limits.py",
    "core/recovery_manager.py",
    "core/sandbox.py",
    "core/validation_engine.py",
    "core/promotion_gate.py",
    "core/version_manager.py",
    "core/emergency_stop.py",
    "core/candidate_generator.py"
]

class PromotionGate:
    """
    Deterministic statistical gate for promoting a candidate to Challenger.
    """
    def __init__(self, ledger_path: str):
        self.ledger = PromotionLedger(ledger_path)
        
    def evaluate_candidate(self, manifest: CandidateManifest, scorecard: ValidationScorecard, champion_metrics: Dict[str, Any], challenger_metrics: Dict[str, Any]) -> str:
        """
        Evaluates if the candidate mathematically beats the champion and respects anchors.
        Returns "APPROVED" or "REJECTED".
        """
        decision = "REJECTED"
        reason = ""
        
        try:
            # 1. Check Trust Anchors
            all_files = manifest.modified_files + manifest.created_files + manifest.deleted_files
            for file_path in all_files:
                # Normalize path for comparison
                patch_path = file_path.replace("\\", "/")
                if patch_path in TRUST_ANCHORS:
                    reason = f"TRUST_ANCHOR_VIOLATION: Attempted to modify {patch_path}"
                    return decision
                    
            # 2. Check 9D.1 Validation Status
            if scorecard.status != "VALIDATED":
                reason = f"VALIDATION_FAILED: Candidate status is {scorecard.status}"
                return decision
                
            # 3. Statistical Benchmark Rules
            acc_champ = champion_metrics.get("accuracy", 0.0)
            acc_chall = challenger_metrics.get("accuracy", 0.0)
            
            reg_rate = challenger_metrics.get("regression_rate", 1.0)
            cost = challenger_metrics.get("cost", 999.0)
            latency = challenger_metrics.get("latency", 999.0)
            sec_violations = challenger_metrics.get("security_violations", 1)
            
            # Thresholds
            MAX_REGRESSION = 0.02
            MAX_COST = 5.0
            MAX_LATENCY = 2.0
            
            if sec_violations > 0:
                reason = "SECURITY_VIOLATION: Benchmark detected security violations."
            elif acc_chall <= acc_champ:
                reason = f"NO_IMPROVEMENT: Challenger accuracy {acc_chall} <= Champion {acc_champ}."
            elif reg_rate > MAX_REGRESSION:
                reason = f"REGRESSION_TOO_HIGH: {reg_rate} > {MAX_REGRESSION}."
            elif cost > MAX_COST:
                reason = f"COST_EXCEEDED: {cost} > {MAX_COST}."
            elif latency > MAX_LATENCY:
                reason = f"LATENCY_EXCEEDED: {latency} > {MAX_LATENCY}."
            else:
                decision = "APPROVED"
                reason = "Mathematically superior to Champion."
                
        finally:
            self.ledger.record_decision({
                "candidate_id": manifest.candidate_id,
                "hypothesis_id": manifest.hypothesis_id,
                "parent_version": manifest.parent_commit,
                "champion_score": champion_metrics.get("accuracy", 0.0),
                "challenger_score": challenger_metrics.get("accuracy", 0.0),
                "resource_metrics": {
                    "latency": challenger_metrics.get("latency", 0),
                    "cost": challenger_metrics.get("cost", 0),
                    "regression_rate": challenger_metrics.get("regression_rate", 0)
                },
                "security_result": "FAIL" if challenger_metrics.get("security_violations", 1) > 0 else "PASS",
                "decision": decision,
                "decision_reason": reason,
                "sample_count": challenger_metrics.get("sample_count", 0)
            })
            
        return decision
