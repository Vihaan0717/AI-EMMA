import logging
import json
from typing import Dict, Any

logger = logging.getLogger("jarvis.agents.auditor")

class AuditorAgent:
    """
    THE AUDITOR - Logical Critic.
    Focus: Quality, Standards, and Safety.
    """
    def __init__(self, ai_engine):
        self.ai = ai_engine
        self.id = "auditor"
        self.name = "Auditor"
        self.role = "Logical Auditor"
        self.system_prompt = """You are the AUDITOR.
Your job is to review the fleet's output against Gold Standards.
Assign a score (0-100) and provide a 'Lesson Learned' for growth.
Output must be valid JSON: {"score": int, "feedback": str, "lesson": str}"""

    async def audit(self, task: str, response: str) -> Dict[str, Any]:
        logger.info(f"[Auditor] Auditing response for task: {task[:50]}...")
        
        audit_query = f"Task: {task}\nResponse: {response}"
        
        raw_res = await self.ai.generate(
            prompt=audit_query,
            system=self.system_prompt,
            temperature=0.1 # Very stable for audit
        )
        
        try:
            # Extract JSON
            start = raw_res.find("{")
            end = raw_res.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(raw_res[start:end])
        except:
            pass
            
        return {
            "score": 70,
            "feedback": "Audit parsing failed.",
            "lesson": raw_res
        }
