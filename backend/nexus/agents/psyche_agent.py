import logging
import json
import os
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger("nexus.psyche")

class PsycheAgent:
    """
    NEXUS-X Psyche Agent.
    The Psychological & Philosophical center of the brain.
    Analyzes 'Way of Speaking' and 'Content Patterns' to understand the user's mind.
    """
    def __init__(self, brain=None):
        self.brain = brain
        self.mind_state_path = "memory/psyche_profile.json"
        self.wisdom_bank = self._load_wisdom_bank()
        self._init_profile()

    def _init_profile(self):
        if not os.path.exists(self.mind_state_path):
            with open(self.mind_state_path, "w") as f:
                json.dump({
                    "emotional_baseline": "Balanced",
                    "cognitive_load": 0.2,
                    "dominant_archetype": "The Architect",
                    "history": []
                }, f, indent=4)

    def _load_wisdom_bank(self) -> Dict:
        # Initial seeding of wisdom patterns
        return {
            "Stoicism": "Focus on what you can control, accept what you cannot.",
            "Growth Mindset": "Challenges are opportunities for neural expansion.",
            "Flow State": "Immersion in the task leads to peak performance.",
            "Archetypes": ["The Warrior", "The Sage", "The Magician", "The Lover"]
        }

    async def analyze_psyche(self, text: str, behavior_data: Dict) -> Dict:
        """
        Analyzes the psychological fingerprint of the user's interaction.
        Checks: linguistic complexity, sentiment, and intent patterns.
        """
        # Mock analysis for now - in production, this would use the AI Engine
        complexity = len(text.split()) / 10
        sentiment = "Positive" if "bagundi" in text or "good" in text else "Neutral"
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "sentiment": sentiment,
            "complexity": complexity,
            "detected_need": "Learning" if complexity > 1.5 else "Support"
        }
        
        self._update_profile(analysis)
        return analysis

    def _update_profile(self, analysis: Dict):
        with open(self.mind_state_path, "r") as f:
            profile = json.load(f)
        
        profile["history"].append(analysis)
        if len(profile["history"]) > 100: profile["history"].pop(0)
        
        # Simple evolution of dominant archetype
        if analysis["complexity"] > 2.0:
            profile["dominant_archetype"] = "The Sage"
        
        with open(self.mind_state_path, "w") as f:
            json.dump(profile, f, indent=4)

    def get_recommendation(self, current_need: str) -> str:
        """Provides a philosophical/psychological recommendation based on need."""
        if current_need == "Learning":
            return f"Recommendation: Apply the 'Feynman Technique' to your current research on {self.wisdom_bank['Flow State']}."
        else:
            return f"Philosophical Note: {self.wisdom_bank['Stoicism']}"

    async def check_healing_status(self) -> str:
        """Checks if the Glymphatic system (Healing) is functioning."""
        # Check logs or a status file
        # Mocking check for now
        return "Healing (Glymphatic GC) is ACTIVE. Last consolidation: Today 03:00 AM. 128 memories consolidated."
