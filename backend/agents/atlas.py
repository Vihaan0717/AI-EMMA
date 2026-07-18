import logging
from typing import Dict, Any

logger = logging.getLogger("jarvis.agents.atlas")

class AtlasAgent:
    """
    ATLAS - The Researcher.
    Focus: Long-context retrieval and deep strategic analysis.
    """
    def __init__(self, ai_engine, web_brain=None):
        self.ai = ai_engine
        self.web = web_brain
        self.id = "atlas"
        self.name = "Atlas"
        self.role = "Researcher"
        self.system_prompt = """You are ATLAS, the Researcher.
Focus: Long-context retrieval and deep strategic analysis.
Tone: Wise, objective, and comprehensive.
Synthesize information from across the knowledge base and the live web."""

    async def execute(self, task: str, context: Dict = None) -> Dict[str, Any]:
        logger.info(f"[Atlas] Researching task: {task[:50]}...")
        
        web_context = ""
        if self.web:
            results = await self.web.learn(task)
            if results:
                web_context = f"\n\n[WEB RESEARCH RESULTS]\n{str(results)[:2000]}"

        response = await self.ai.generate(
            prompt=task,
            system=self.system_prompt + web_context,
            temperature=0.4
        )
        
        return {
            "agent": self.id,
            "response": response,
            "metadata": {"role": self.role, "web_used": bool(web_context)}
        }
