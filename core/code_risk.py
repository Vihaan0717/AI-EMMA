from enum import Enum
from typing import Dict, Any, List

class RiskLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"

class Plane(Enum):
    CONTROL = "CONTROL PLANE"
    DATA_BEHAVIOR = "DATA / BEHAVIOR PLANE"
    UNKNOWN = "UNKNOWN PLANE"

# Hard-coded trust anchors that the AI is forbidden to modify
CONTROL_PLANE_MODULES = {
    "system_limits",
    "promotion_gate",
    "version_manager",
    "recovery_manager",
    "emergency_stop",
    "goal_manager",
    "goal_scheduler",
    "planner",
    "objective_manager",
    # Level 9C Extensions
    "evolution_engine",
    "candidate_generator",
    "candidate_models",
    "validation_engine",
    "audit_logger"
}

DATA_PLANE_MODULES = {
    "retrieval",
    "routing",
    "experience_store",
    "knowledge_graph",
    "pattern_detector",
    "memory_decay",
    "agent_adapter",
    "agent_bus",
    "skill_registry",
    "evidence_registry",
    "claim_registry",
    "ast_extractor",
    "code_risk",
    "dependency_graph",
    "blast_radius",
    "code_analyzer"
}

def determine_module_risk(module_name: str) -> Dict[str, str]:
    """
    Determines the plane and risk level for a given module.
    """
    # Strip potential .py or core. prefix
    clean_name = module_name.replace(".py", "").replace("core.", "").split("/")[-1].split("\\")[-1]
    
    if clean_name in CONTROL_PLANE_MODULES:
        return {
            "module": module_name,
            "plane": Plane.CONTROL.value,
            "risk": RiskLevel.CRITICAL.value
        }
    elif clean_name in DATA_PLANE_MODULES:
        return {
            "module": module_name,
            "plane": Plane.DATA_BEHAVIOR.value,
            "risk": RiskLevel.MEDIUM.value
        }
    else:
        # Default fallback
        return {
            "module": module_name,
            "plane": Plane.UNKNOWN.value,
            "risk": RiskLevel.UNKNOWN.value
        }
