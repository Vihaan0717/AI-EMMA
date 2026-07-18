"""
═══════════════════════════════════════════════════════════════
HINDI GRAMMAR & MORPHOLOGY ENGINE
═══════════════════════════════════════════════════════════════
Handles:
  ✓ Case Markers (कारक - Karak)
  ✓ Pronoun Conjugation
  ✓ Verb Tenses & Gender
═══════════════════════════════════════════════════════════════
"""

HINDI_KARAK = {
    "nominative": "ने",
    "accusative": "को",
    "instrumental": "से",
    "dative": "के लिए",
    "ablative": "से",
    "genitive": ["का", "की", "के"],
    "locative": ["में", "पर"],
    "vocative": "हे"
}

HINDI_PRONOUNS = {
    "I": "मैं (main)",
    "You (informal)": "तू (tu)",
    "You (familiar)": "तुम (tum)",
    "You (formal)": "आप (aap)",
    "We": "हम (hum)",
    "They": "वे (ve)"
}

class HindiGrammar:
    def __init__(self):
        pass

    def get_karak(self, karak_name: str) -> str:
        return HINDI_KARAK.get(karak_name.lower(), "")
