
"""
ReinforcementEngine (Frontal/Synaptic) — ARION's Learning from Experience.
Adjusts behavioral weights based on owner feedback and engagement.
"""

import os
import json
from pathlib import Path
from datetime import datetime

class ReinforcementEngine:

    def __init__(self, profile_path: str = "arion/data/brain/behavior_profile.json"):
        self.profile_path = Path(profile_path)
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        self.profile = self._load_profile()
        print(f"[ReinforcementEngine] Synaptic learning online. Adaptive weights loaded.", flush=True)

    def _load_profile(self) -> dict:
        if self.profile_path.exists():
            try:
                with open(self.profile_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        
        # Default behavior profile (neutral baseline)
        return {
            "weights": {
                "sarcasm":    0.5,
                "mirroring":  0.7,
                "shortness":  0.6,
                "empathy":    0.5,
                "technical":  0.3,
            },
            "signals": {
                "positive": 0,
                "negative": 0,
            },
            "learned_preferences": [],
            "last_updated": datetime.now().isoformat()
        }

    def process_feedback(self, text: str, sentiment: float):
        """
        Adjusts weights based on explicit or implicit feedback.
        sentiment: 1.0 (very positive) to -1.0 (very negative)
        """
        # Logic to detect keywords in feedback
        tl = text.lower()
        mapping = {
            "sarcasm":   ["sarcastic", "taunt", "funny", "joke"],
            "shortness": ["short", "brief", "too long", "too much"],
            "empathy":   ["caring", "sweet", "nice", "rude", "cold"],
        }
        
        adjustment = sentiment * 0.05
        
        for weight, keywords in mapping.items():
            if any(k in tl for k in keywords):
                old = self.profile["weights"].get(weight, 0.5)
                # If negative sentiment and "too much" of something, reduce it.
                # If positive sentiment and they like it, increase it.
                new_val = max(0.0, min(1.0, old + adjustment))
                self.profile["weights"][weight] = new_val
        
        if sentiment > 0:
            self.profile["signals"]["positive"] += 1
        elif sentiment < 0:
            self.profile["signals"]["negative"] += 1
            
        self._save_profile()

    def get_behavior_instructions(self) -> str:
        """Generates raw system prompt instructions based on learned profile."""
        w = self.profile["weights"]
        
        instructions = [
            f"Sarcasm weight: {w['sarcasm']:.1f}.",
            f"Mirroring weight: {w['mirroring']:.1f}.",
            f"Brevity weight: {w['shortness']:.1f} (high means very short codes/one-liners).",
            f"Technical depth: {w['technical']:.1f}.",
        ]
        
        if self.profile["learned_preferences"]:
            instructions.append("\nLEARNED PREFERENCES:")
            for p in self.profile["learned_preferences"][-5:]: # Last 5
                instructions.append(f"- {p}")
                
        return "\n".join(instructions)

    def _save_profile(self):
        self.profile["last_updated"] = datetime.now().isoformat()
        with open(self.profile_path, "w", encoding="utf-8") as f:
            json.dump(self.profile, f, indent=2)
