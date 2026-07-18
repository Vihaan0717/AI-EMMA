import json
import datetime
import os
import logging

logger = logging.getLogger("NexusLearner")

class NexusLearner:
    """
    T7 Memory Layer: Manages the 'Linguistic DNA' of NEXUS-X.
    Transitions the AI from a tool to a student.
    """
    def __init__(self, brain_file='data/telugu_dna.json'):
        self.brain_file = brain_file
        self.dna = self._load_dna()

    def _load_dna(self):
        if os.path.exists(self.brain_file):
            try:
                with open(self.brain_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load DNA: {e}")
        return {"vocabulary": {}, "slang_registry": {}, "tutorial_patterns": {}}

    def learn(self, phrase, meaning, context="slang", dialect="General"):
        """
        Registers a new phrase into the DNA.
        Categorizes based on dialect and context.
        """
        timestamp = datetime.datetime.now().isoformat()
        
        # Check if already exists to increase strength
        registry_key = "vocabulary"
        if dialect != "General" or context == "slang":
            registry_key = "slang_registry"
        elif any(tech in context.lower() for tech in ["html", "css", "js", "python"]):
            registry_key = "tutorial_patterns"

        if phrase in self.dna[registry_key]:
            if "strength" in self.dna[registry_key][phrase]:
                self.dna[registry_key][phrase]["strength"] += 1
            self.dna[registry_key][phrase]["last_used"] = timestamp
            action = "reinforced"
        else:
            if registry_key == "slang_registry":
                self.dna[registry_key][phrase] = {
                    "meaning": meaning,
                    "dialect": dialect,
                    "social_tier": "informal",
                    "usage": f"{phrase.capitalize()} boss?"
                }
            elif registry_key == "tutorial_patterns":
                self.dna[registry_key][phrase] = meaning
            else:
                self.dna[registry_key][phrase] = {
                    "meaning": meaning,
                    "context": context,
                    "strength": 1,
                    "last_used": timestamp
                }
            action = "registered"

        self._save_dna()
        return f"NEXUS-X: '{phrase}' {action} in DNA. Learning complete."

    def _save_dna(self):
        try:
            with open(self.brain_file, 'w', encoding='utf-8') as f:
                json.dump(self.dna, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save DNA: {e}")

    def get_discovery_list(self):
        """Returns phrases with low strength for A10 Sandbox analysis."""
        discovery = []
        for category in self.dna.values():
            for phrase, data in category.items():
                # Use .get() to avoid KeyError if strength is missing
                if isinstance(data, dict) and data.get("strength", 0) < 2:
                    discovery.append(phrase)
        return discovery

if __name__ == "__main__":
    learner = NexusLearner()
    print(learner.learn("nerchukundham", "let's learn", "tutorial_intro"))
    print(learner.learn("kaiku", "why", "slang", "Hyderabad"))
