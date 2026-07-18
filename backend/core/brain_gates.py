import logging
import time
import os
from typing import Dict, List, Tuple, Any

logger = logging.getLogger("BrainGates")

class ThalamicGate:
    """
    Biological Analog: Thalamus (Sensory Gating)
    Filters noise, scores salience, and routes signals to appropriate cortical areas.
    """
    def __init__(self, salience_threshold: float = 0.2):
        self.salience_threshold = salience_threshold

    def score_salience(self, text: str, context: Dict) -> float:
        """
        Scores how important this input is based on length, complexity, 
        and relevance to active context.
        """
        score = 0.0
        
        # 1. Complexity (length and variety)
        score += min(0.4, len(text.split()) / 20.0)
        
        # 2. Urgency keywords
        urgency_words = ["now", "urgent", "help", "security", "emergency", "boss"]
        if any(w in text.lower() for w in urgency_words):
            score += 0.5
            
        # 3. Direct Questions
        if "?" in text:
            score += 0.2
            
        # 4. Authority override (Owner/Admin always gets a response)
        sender = context.get("sender", "").lower()
        admin_num = os.getenv("ADMIN_NUMBER", "").strip()
        
        is_admin = (
            "owner" in sender or 
            "admin" in sender or 
            sender == "arion" or 
            sender == "jarvis" or
            (admin_num and admin_num in sender)
        )
        
        if is_admin:
            score = max(score, 0.5)
            
        return min(1.0, score)

    async def process(self, data: Dict) -> Dict:
        text = data.get("raw_input", "")
        salience = self.score_salience(text, data.get("context", {}))
        
        data["salience_score"] = salience
        
        if salience < self.salience_threshold:
            logger.info(f"[Thalamus] Low salience ({salience:.2f}). Routing to background logging.")
            data["route"] = "background"
        elif salience > 0.8:
            logger.info(f"[Thalamus] High salience ({salience:.2f}). Priority routing active.")
            data["route"] = "priority"
        else:
            data["route"] = "cortex"
            
        return data

class PredictiveGate:
    """
    Biological Analog: Predictive Coding
    Anti-hallucination firewall that rejects or flags inputs that contradict the world model.
    """
    def __init__(self, contradiction_threshold: int = 3):
        self.contradiction_threshold = contradiction_threshold

    async def gate(self, text: str, memories: List[Dict]) -> Tuple[bool, str, float]:
        """
        Compares input against recalled memories to detect contradictions.
        Returns: (passed, reason, confidence)
        """
        # In a real implementation, we would use an LLM or cross-referencing model here.
        # For now, we use a semantic similarity check (mocked for the blueprint).
        
        contradictions = 0
        for mem in memories:
            # Mock contradiction check: if memory content says "X is Y" 
            # and input says "X is not Y" (simplified)
            # This would ideally use NLI (Natural Language Inference)
            pass

        # Placeholder logic: If we find direct contradictions in memories
        if contradictions >= self.contradiction_threshold:
            return False, "contradicts_world_model", 0.1
            
        return True, "consistent", 0.9

    async def process(self, data: Dict) -> Dict:
        if "memories" not in data:
            return data
            
        text = data.get("normalized_text", "")
        passed, reason, confidence = await self.gate(text, data["memories"])
        
        data["prediction_gate"] = {
            "passed": passed,
            "reason": reason,
            "confidence": confidence
        }
        
        if not passed:
            logger.warning(f"[PredictiveGate] REJECTED: {reason} (Confidence: {confidence:.2f})")
            
        return data
