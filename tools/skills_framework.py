import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

logger = logging.getLogger("SkillsFramework")

class BaseSkill(ABC):
    """
    Abstract base class for all pluggable agent Skills.
    Ensures safe parameter validation, standard return interfaces, and consistent logging.
    """
    def __init__(self, name: str, description: str, required_args: List[str]):
        self.name = name
        self.description = description
        self.required_args = required_args

    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validates that all required arguments are present and non-empty."""
        for arg in self.required_args:
            if arg not in args or args[arg] is None:
                logger.warning(f"Skill '{self.name}': Missing required argument '{arg}'")
                return False
        return True

    @abstractmethod
    def run(self, args: Dict[str, Any]) -> str:
        """Executes the skill's action. Must be overridden by subclasses."""
        pass

    def execute(self, args: Dict[str, Any]) -> str:
        """Wrapper method that enforces validation and safety before execution."""
        if not self.validate_args(args):
            return f"Error: Missing one of the required arguments: {self.required_args}"
        try:
            logger.info(f"Skill '{self.name}': Initiating execution...")
            return self.run(args)
        except Exception as e:
            logger.error(f"Skill '{self.name}' execution failed: {e}", exc_info=True)
            return f"Execution Failure in {self.name}: {str(e)}"

class SkillRegistry:
    """
    Manages and registers active agent Skills.
    """
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}

    def register_skill(self, skill: BaseSkill):
        self._skills[skill.name] = skill
        logger.info(f"Registered Skill: {skill.name} - {skill.description}")

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        return self._skills.get(name)

    def list_skills(self) -> List[Dict[str, Any]]:
        return [{"name": s.name, "description": s.description} for s in self._skills.values()]
