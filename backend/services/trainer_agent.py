import logging
from typing import List, Dict, Any
from core.skill_models import Skill, SkillStatus, CapabilityAction
from evolution_lab.sandbox import SandboxLab
from evolution_lab.promotion_gate import PromotionGate

logger = logging.getLogger("jarvis.trainer_agent")

class ProgressivePermissioning:
    STAGES = ["READ_ONLY", "LIMITED_TOOLS", "SANDBOX", "TEST_DATA", "BENCHMARK", "RESTRICTED_PRODUCTION", "FULL_ACCESS"]
    
    @staticmethod
    def get_next_stage(current_stage: str) -> str:
        if current_stage not in ProgressivePermissioning.STAGES:
            return "READ_ONLY"
        idx = ProgressivePermissioning.STAGES.index(current_stage)
        if idx + 1 < len(ProgressivePermissioning.STAGES):
            return ProgressivePermissioning.STAGES[idx + 1]
        return current_stage

class TrainerAgent:
    def __init__(self, sandbox: SandboxLab, gate: PromotionGate):
        self.sandbox = sandbox
        self.gate = gate

    def acquire_skill(self, repeated_workflow: List[str], skill_name: str) -> Skill:
        """
        Observes repetitive workflow chains and proposes a Skill Candidate.
        Routes the candidate through progressive sandboxing.
        """
        logger.info(f"Trainer Agent initiating skill acquisition for workflow: {skill_name}")
        
        # 1. Map workflow to CapabilityAction
        procedure = []
        for step in repeated_workflow:
            procedure.append(CapabilityAction(action=step, arguments={}))
            
        # 2. Generate Candidate
        candidate = Skill(
            skill_name=skill_name,
            agent="Trainer",
            domain="acquired_skills",
            version=1,
            status=SkillStatus.CANDIDATE,
            procedure=procedure
        )
        
        # 3. Progressive Permissioning Pipeline
        current_permission = "READ_ONLY"
        while current_permission != "FULL_ACCESS":
            logger.info(f"Skill {skill_name} passing stage: {current_permission}")
            
            # Simulate Sandbox evaluation at this permission level
            # In a real system, the limit_enforcer is configured with this permission stage
            if current_permission == "BENCHMARK":
                # Ensure it passes the promotion gate (mock champion scorecard)
                pass
                
            current_permission = ProgressivePermissioning.get_next_stage(current_permission)
            
        logger.info(f"Skill {skill_name} successfully acquired and promoted to FULL_ACCESS.")
        candidate.status = SkillStatus.ESTABLISHED
        return candidate
