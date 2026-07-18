import logging

logger = logging.getLogger("jarvis.language.tenglish")

class TenglishMapper:
    """
    Maps Romanized Telugu (Tenglish) phrases to semantic meanings.
    Focuses on Hyderabad/Andhra slang.
    """
    
    SLANG_MAP = {
        "bagunnava": "How are you? (Friendly)",
        "em chesthunnav": "What are you doing?",
        "thinnava": "Did you eat?",
        "baigan": "Nonsense/Typical Hyderabad filler",
        "hau": "Yes (Deccani/Hyderabad style)",
        "nakko": "No/Don't want (Deccani/Hyderabad style)",
        "kiraak": "Awesome/Excellent"
    }

    def parse_slang(self, text: str) -> dict:
        """Detect and map slang in the text."""
        text_l = text.lower()
        found = {}
        
        for slang, meaning in self.SLANG_MAP.items():
            if slang in text_l:
                found[slang] = meaning
                
        return {
            "is_tenglish": len(found) > 0,
            "mapped_slang": found,
            "tone": "casual" if len(found) > 0 else "standard"
        }
