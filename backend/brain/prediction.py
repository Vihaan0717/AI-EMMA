import logging
from collections import Counter

logger = logging.getLogger("jarvis.brain.prediction")

class PredictionEngine:
    """
    Anticipates user's next topics based on sequence history.
    Proactively helps by pre-fetching knowledge or adjusting context.
    """
    def __init__(self):
        self.history = []
        self.transition_matrix = {} # topic -> {next_topic: count}

    def record_transition(self, previous_topic: str, current_topic: str):
        """Build the transition model over time."""
        if previous_topic not in self.transition_matrix:
            self.transition_matrix[previous_topic] = Counter()
        self.transition_matrix[previous_topic][current_topic] += 1
        self.history.append(current_topic)

    def predict_next(self, current_topic: str) -> list[str]:
        """Predict top 3 likely next topics."""
        if current_topic not in self.transition_matrix:
            # Fallback to general history frequency
            return [t for t, c in Counter(self.history).most_common(3)]
        
        top_transitions = self.transition_matrix[current_topic].most_common(3)
        return [t for t, c in top_transitions]

    def get_proactive_hint(self, current_topic: str) -> str:
        """Returns a proactive help string for the UI."""
        predictions = self.predict_next(current_topic)
        if not predictions:
            return ""
        
        # Example logic from the plan
        mapping = {
            "agent sync": ["logs", "memory issue", "async problem"],
            "telugu": ["slang", "translation", "cultural context"],
            "code": ["debug", "refactor", "optimization"]
        }
        
        for p in predictions:
            if p in mapping:
                return f"Hint: You might want to check {mapping[p][0]} next."
        
        return f"Predicted path: {' -> '.join(predictions)}"
