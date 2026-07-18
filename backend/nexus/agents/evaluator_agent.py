import logging
import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger("nexus.evaluator")

@dataclass
class InteractionRecord:
    timestamp: str
    user_input: str
    agent_response: str
    feedback: Optional[str] = None
    sentiment: float = 0.0
    score: float = 0.5
    correction_extracted: Optional[str] = None

class EvaluatorAgent:
    """
    Local Evaluator Agent — The "Self-Awareness" Layer.
    Monitors user feedback and scores responses to improve future accuracy.
    """
    def __init__(self, log_path: str = "data/learning_logs/feedback_loop.json"):
        self.log_path = log_path
        self._ensure_log_dir()
        self.feedback_keywords = {
            "positive": ["correct", "better", "nice", "good", "yes", "exactly", "correct ga"],
            "negative": ["wrong", "incorrect", "bad", "no", "not this", "tappu", "kadhu"],
            "correction": ["it should be", "instead of", "use this", "idi kadhu", "idi correct"]
        }

    def _ensure_log_dir(self):
        import os
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_logs(self) -> List[Dict]:
        with open(self.log_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_logs(self, logs: List[Dict]):
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)

    async def evaluate_feedback(self, user_input: str, last_interaction: Dict) -> Optional[InteractionRecord]:
        """
        Analyzes current user input for feedback regarding the previous interaction.
        """
        feedback_type = self._detect_feedback_type(user_input)
        if not feedback_type:
            return None

        score = 0.5
        if feedback_type == "positive":
            score = 0.9
        elif feedback_type == "negative":
            score = 0.1
        elif feedback_type == "correction":
            score = 0.3

        record = InteractionRecord(
            timestamp=datetime.datetime.now().isoformat(),
            user_input=last_interaction.get("query", ""),
            agent_response=last_interaction.get("answer", ""),
            feedback=user_input,
            score=score,
            correction_extracted=self._extract_correction(user_input) if feedback_type == "correction" else None
        )

        self._log_interaction(record)
        return record

    def _detect_feedback_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for category, keywords in self.feedback_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return category
        return None

    def _extract_correction(self, text: str) -> str:
        """Simple heuristic to extract the corrected part."""
        # Future: Use LLM for precise extraction
        return text.replace("it should be", "").replace("idi correct", "").strip()

    def _log_interaction(self, record: InteractionRecord):
        logs = self._load_logs()
        logs.append(asdict(record))
        # Keep only last 1000 interactions
        self._save_logs(logs[-1000:])
        logger.info(f"Evaluator: Logged feedback loop entry (Score: {record.score})")

    def get_learning_patterns(self, min_score: float = 0.8) -> List[Dict]:
        """Returns interactions that were highly rated to be used as patterns."""
        logs = self._load_logs()
        return [log for log in logs if log.get("score", 0) >= min_score]

    def get_corrections(self) -> List[Dict]:
        """Returns interactions where corrections were provided."""
        logs = self._load_logs()
        return [log for log in logs if log.get("correction_extracted")]
