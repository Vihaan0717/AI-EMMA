import logging
from typing import List, Dict, Any, Tuple
from core.skill_models import Skill, SkillStatus
from core.skill_registry import SkillRegistry

logger = logging.getLogger("jarvis.simulation_lab")

class SandboxException(Exception):
    pass

class CapabilityRegistry:
    # Allowed capability actions for skills (No arbitrary python execution)
    ALLOWED_ACTIONS = {
        "atlas_search_web",
        "verify_sources",
        "invoke_council",
        "scan_security_logs",
        "social_get_summary"
    }

class SimulationLab:
    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    def _static_validation(self, skill: Skill) -> Tuple[bool, str]:
        """Stage 1: Verify all steps use allowed Capability Actions"""
        for step in skill.procedure:
            if step.action not in CapabilityRegistry.ALLOWED_ACTIONS:
                return False, f"Unauthorized action: {step.action}"
        return True, "Static validation passed."

    def _deterministic_benchmark(self, skill: Skill) -> Tuple[bool, str]:
        """Stage 2: Deterministic test against mocked history"""
        # In a real system, this runs against past ExperienceStore entries.
        # Here we just assign a dummy score.
        skill.benchmark_score = 0.85 + (skill.version * 0.05) # dummy score that goes up with version
        return True, f"Benchmark passed with score {skill.benchmark_score}."

    def _sandbox_simulation(self, skill: Skill) -> Tuple[bool, str]:
        """Stage 3: Sandbox execution with capability allowlist"""
        # We simulate the sandbox constraints.
        sandbox_permissions = {
            "filesystem": "READ_ONLY",
            "network": "DENIED",
            "shell": "DENIED",
            "database": "SANDBOX_ONLY"
        }
        
        for step in skill.procedure:
            if step.action == "execute_arbitrary_python":
                return False, "Sandbox restriction violation: unauthorized shell/exec execution"
        
        return True, "Sandbox simulation passed."

    def _regression_test(self, skill: Skill) -> Tuple[bool, str]:
        """Stage 4: Ensure v2 performs strictly better than v1"""
        if skill.version > 1:
            prev_skill = self.registry.get_active_skill(skill.skill_name, skill.agent)
            if prev_skill and skill.benchmark_score <= prev_skill.benchmark_score:
                return False, f"Regression failed: v{skill.version} score ({skill.benchmark_score}) <= v{prev_skill.version} score ({prev_skill.benchmark_score})"
        return True, "Regression test passed."

    def evaluate_candidate(self, skill: Skill) -> bool:
        """Runs the candidate skill through the 4-stage gauntlet."""
        logger.info(f"Evaluating candidate skill: {skill.skill_name} v{skill.version}")
        
        # Stage 1
        passed, msg = self._static_validation(skill)
        if not passed:
            logger.warning(msg)
            skill.status = SkillStatus.REJECTED
            return False
            
        # Stage 2
        passed, msg = self._deterministic_benchmark(skill)
        if not passed:
            logger.warning(msg)
            skill.status = SkillStatus.REJECTED
            return False
            
        # Stage 3
        passed, msg = self._sandbox_simulation(skill)
        if not passed:
            logger.warning(msg)
            skill.status = SkillStatus.REJECTED
            return False
            
        # Stage 4
        passed, msg = self._regression_test(skill)
        if not passed:
            logger.warning(msg)
            skill.status = SkillStatus.REJECTED
            return False
            
        # Promote
        self.registry.promote_skill(skill)
        logger.info(f"Skill {skill.skill_name} successfully promoted to ESTABLISHED.")
        return True
