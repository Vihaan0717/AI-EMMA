import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger("jarvis.version_manager")

class SystemManifest(BaseModel):
    core: str = "1.0.0"
    router: str = "1.0.0"
    research: str = "1.0.0"
    retrieval: str = "1.0.0"
    memory: str = "1.0.0"
    policies: str = "1.0.0"

class VersionManager:
    def __init__(self, ledger_path: str = "logs/promotions.db"):
        self.active_manifest = SystemManifest()
        self.history = [self.active_manifest]
        self.baseline_failure_rate = 0.041 # 4.1%
        
        # Current deployment stats
        self.canary_observations = 0
        self.canary_failures = 0
        
        # Canary Phases
        self.canary_stages = [0.01, 0.05, 0.10, 0.25, 0.50, 1.00]
        self.current_stage_idx = 0
        
        self.ledger_path = ledger_path

    def get_manifest(self) -> SystemManifest:
        return self.active_manifest

    def deploy_manifest(self, new_manifest: SystemManifest):
        self.history.append(self.active_manifest)
        self.active_manifest = new_manifest
        self.canary_observations = 0
        self.canary_failures = 0
        self.current_stage_idx = 0
        logger.info(f"Deployed new System Manifest: {new_manifest.model_dump_json()} at canary stage {self.get_traffic_percentage() * 100}%")
        
    def get_traffic_percentage(self) -> float:
        if self.current_stage_idx < len(self.canary_stages):
            return self.canary_stages[self.current_stage_idx]
        return 1.0

    def record_canary_observation(self, failed: bool, candidate_id: str = ""):
        """
        Monitors the current manifest. Triggers rollback or promotes to next stage.
        """
        self.canary_observations += 1
        if failed:
            self.canary_failures += 1
            
        # Mathematical thresholds per stage
        MIN_OBSERVATIONS = 100
        ROLLBACK_THRESHOLD = 0.087
        
        if self.canary_observations >= MIN_OBSERVATIONS:
            failure_rate = self.canary_failures / self.canary_observations
            if failure_rate >= ROLLBACK_THRESHOLD:
                logger.critical(f"CANARY FAILURE: Failure rate {failure_rate:.3f} >= {ROLLBACK_THRESHOLD}. Initiating Rollback.")
                self.rollback(candidate_id, f"Canary failure rate {failure_rate:.3f} exceeded threshold {ROLLBACK_THRESHOLD}")
            else:
                # Stage promotion
                if self.current_stage_idx < len(self.canary_stages) - 1:
                    self.current_stage_idx += 1
                    logger.info(f"CANARY PROMOTION: Advancing to {self.get_traffic_percentage() * 100}% traffic.")
                    self.canary_observations = 0
                    self.canary_failures = 0
                elif self.current_stage_idx == len(self.canary_stages) - 1:
                    logger.info("CANARY COMPLETE: Candidate is now 100% Active Champion.")
                    self.current_stage_idx += 1

    def rollback(self, candidate_id: str, reason: str):
        if len(self.history) > 1:
            logger.info("Rolling back to previous manifest.")
            self.active_manifest = self.history.pop()
            self.canary_observations = 0
            self.canary_failures = 0
            self.current_stage_idx = len(self.canary_stages) # back to 100% active for champion
            
            # Record rollback in ledger
            if candidate_id:
                from core.promotion_ledger import PromotionLedger
                ledger = PromotionLedger(self.ledger_path)
                ledger.mark_rollback(candidate_id, reason)
        else:
            logger.error("Cannot rollback. No history available.")
