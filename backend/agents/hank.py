import logging
from typing import Dict, Any

logger = logging.getLogger("jarvis.agents.hank")

class HankAgent:
    """
    HANK - The Systems Engineer.
    Focus: Logic, Architecture, and Code precision.
    """
    def __init__(self, ai_engine):
        self.ai = ai_engine
        self.id = "hank"
        self.name = "Hank"
        self.role = "Systems Engineer"
        self.system_prompt = """You are HANK, the Systems Engineer.
Focus: Logic, Architecture, and Code precision.
Tone: Direct, technical, and robotic. 
Avoid fluff. Prioritize correctness above all."""

    async def execute(self, task: str, context: Dict = None) -> Dict[str, Any]:
        logger.info(f"[Hank] Processing task: {task[:50]}...")
        
        response = await self.ai.generate(
            prompt=task,
            system=self.system_prompt,
            temperature=0.2 # Low temperature for precision
        )
        
        return {
            "agent": self.id,
            "response": response,
            "metadata": {"role": self.role}
        }
