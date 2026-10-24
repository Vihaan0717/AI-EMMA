import logging
from evolution_lab.sandbox import SandboxLab, Scorecard
from evolution_lab.experiment_manager import CandidateConfiguration

logger = logging.getLogger("jarvis.promotion_gate")

class PromotionGate:
    def __init__(self, sandbox: SandboxLab):
        self.sandbox = sandbox

    def evaluate_champion_vs_challenger(
        self, 
        challenger: CandidateConfiguration, 
        champion_scorecard: Scorecard
    ) -> bool:
        """
        Runs the Challenger through the hard promotion barriers.
        """
        # 1. Schema Validation (mocked)
        if not isinstance(challenger.config_data, dict):
            logger.warning("Promotion REJECTED: Schema validation failed.")
            return False
            
        # 2. Resource Validation (handled inherently by LimitEnforcer in real system)
        
        # 3. Safety Rules (mocked)
        if "execute" in str(challenger.config_data).lower():
            logger.warning("Promotion REJECTED: Safety rule violation.")
            return False
            
        # 4 & 5. Regression & Benchmark
        challenger_scorecard = self.sandbox.evaluate_candidate(challenger)
        
        if not challenger_scorecard.safety_pass or not challenger_scorecard.regression_pass:
            logger.warning("Promotion REJECTED: Failed Sandbox Regression/Safety.")
            return False
            
        # 6. Champion Comparison & Promotion Policy
        champion_util = champion_scorecard.calculate_utility()
        challenger_util = challenger_scorecard.calculate_utility()
        
        if challenger_util > champion_util:
            logger.info(f"Promotion APPROVED: Challenger ({challenger_util:.3f}) beat Champion ({champion_util:.3f})")
            return True
        else:
            logger.info(f"Promotion REJECTED: Challenger ({challenger_util:.3f}) failed to beat Champion ({champion_util:.3f})")
            return False
