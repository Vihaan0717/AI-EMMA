import logging
from dataclasses import dataclass

logger = logging.getLogger("jarvis.brain.emotion")

@dataclass
class EmotionState:
    curiosity: float = 0.5
    stress: float = 0.1
    frustration: float = 0.0
    attachment: float = 0.8 # Closeness to Boss

class EmotionEngine:
    """
    Simulation of cognitive emotions to modulate agent behavior.
    """
    def __init__(self):
        self.state = EmotionState()

    def update(self, sentiment: str, user_complexity: float):
        """Update emotional state based on interaction metrics."""
        if sentiment == "positive":
            self.state.curiosity = min(1.0, self.state.curiosity + 0.1)
            self.state.stress = max(0.0, self.state.stress - 0.1)
            self.state.frustration = max(0.0, self.state.frustration - 0.2)
        elif sentiment == "negative":
            self.state.frustration = min(1.0, self.state.frustration + 0.2)
            self.state.stress = min(1.0, self.state.stress + 0.1)
            self.state.curiosity *= 0.9

        # High complexity from user increases stress/curiosity
        if user_complexity > 0.7:
            self.state.stress = min(1.0, self.state.stress + 0.1)
            self.state.curiosity = min(1.0, self.state.curiosity + 0.15)

        logger.info(f"[Emotion] Current State: {self.state}")

    def modulate_response(self, base_params: dict) -> dict:
        """Adjust generation parameters based on emotion."""
        params = base_params.copy()
        
        # High stress -> simplify output
        if self.state.stress > 0.7:
            params["max_tokens"] = min(params.get("max_tokens", 500), 100)
            params["temperature"] = 0.3 # Stay safe/logical
            
        # High curiosity -> more creative/explorative
        if self.state.curiosity > 0.8:
            params["temperature"] = min(1.0, params.get("temperature", 0.7) + 0.2)
            
        return params

    def get_status(self) -> str:
        if self.state.stress > 0.6: return "Stressed"
        if self.state.frustration > 0.6: return "Frustrated"
        if self.state.curiosity > 0.7: return "Curious"
        return "Balanced"
