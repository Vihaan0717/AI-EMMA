import logging

logger = logging.getLogger("RewardModel")

class LocalRewardModel:
    """
    Interface for local Reward Models from Hugging Face.
    Used to objectively score agent responses.
    """
    def __init__(self, model_name="OpenAssistant/reward-model-deberta-v3-large-v2"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._initialized = False # Always start with heuristic to save RAM

    def initialize(self):
        """Loads the model locally using transformers."""
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            logger.info(f"Loading Reward Model: {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
            self._initialized = True
            logger.info("Reward Model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load Reward Model: {e}. Falling back to heuristic scoring.")

    def score(self, task: str, response: str) -> float:
        """
        Scores a response based on helpfulness/accuracy.
        Returns a value between 0 and 100.
        """
        if not self._initialized:
            # Heuristic Fallback
            return self._heuristic_score(task, response)
        
        try:
            import torch
            inputs = self.tokenizer(task, response, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Assuming the model outputs a single scalar score
                score = outputs.logits[0].item()
                # Normalize score to 0-100 (Simplified)
                normalized_score = max(0, min(100, (score + 5) * 10))
                return normalized_score
        except Exception as e:
            logger.error(f"Scoring error: {e}")
            return self._heuristic_score(task, response)

    def _heuristic_score(self, task: str, response: str) -> float:
        """Simple rule-based scoring as a fallback."""
        score = 70.0
        # Reward length and presence of technical keywords
        if len(response) > 50: score += 5
        if "```" in response: score += 10
        if "result" in response.lower() or "solution" in response.lower(): score += 5
        
        # Penalty for 'ai-isms'
        ai_isms = ["as an ai", "i don't have feelings", "language model"]
        for ism in ai_isms:
            if ism in response.lower():
                score -= 20
                
        return max(0, min(100, score))

# Global instance
reward_model = LocalRewardModel()
