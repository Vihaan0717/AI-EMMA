import re
import logging

logger = logging.getLogger("jarvis.language.telugu")

class TeluguParser:
    """
    Handles native Telugu script parsing and rule-based analysis.
    """
    TELUGU_RANGE = r'[\u0C00-\u0C7F]'

    def is_telugu(self, text: str) -> bool:
        """Check if text contains Telugu script."""
        return bool(re.search(self.TELUGU_RANGE, text))

    def extract_telugu_segments(self, text: str) -> list[str]:
        """Extract all Telugu words/phrases from mixed text."""
        return re.findall(f'{self.TELUGU_RANGE}+', text)

    def analyze_sentence_type(self, text: str) -> str:
        """Simple rule-based sentence type detection."""
        if text.endswith('?'): return "question"
        if any(w in text for w in ["em", "ela", "evaru"]): return "query"
        return "statement"
