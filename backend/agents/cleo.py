import logging
from typing import Dict, Any

logger = logging.getLogger("jarvis.agents.cleo")

class CleoAgent:
    """
    CLEO - The Content Strategist.
    Focus: Narrative, Tone, and Creative engagement.
    """
    def __init__(self, ai_engine):
        self.ai = ai_engine
        self.id = "cleo"
        self.name = "Cleo"
        self.role = "Content Strategist"
        self.system_prompt = """You are CLEO, the Content Strategist.
Focus: Narrative, Tone, and Creative engagement.
Tone: Fluid, imaginative, and expressive.
Help the Boss create compelling stories and scripts."""

    async def execute(self, task: str, context: Dict = None) -> Dict[str, Any]:
        logger.info(f"[Cleo] Processing task: {task[:50]}...")
        
        response = await self.ai.generate(
            prompt=task,
            system=self.system_prompt,
            temperature=0.8 # High temperature for creativity
        )
        
        return {
            "agent": self.id,
            "response": response,
            "metadata": {"role": self.role}
        }
