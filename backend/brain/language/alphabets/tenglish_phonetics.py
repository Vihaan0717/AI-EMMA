"""
═══════════════════════════════════════════════════════════════
TENGLISH PHONETICS ENGINE
═══════════════════════════════════════════════════════════════
Logic for mapping Telugu script to Romanized Tenglish and back.
Handles common WhatsApp-style spelling variations.
═══════════════════════════════════════════════════════════════
"""

from .telugu_alphabet import TELUGU_VOWELS, TELUGU_CONSONANTS, TELUGU_MATRAS

class TenglishPhonetics:
    def __init__(self):
        self.char_to_roman = self._build_map()
        self.roman_to_char = {v: k for k, v in self.char_to_roman.items()}
        
        # Common Tenglish slang/shortcuts
        self.common_mappings = {
            "naku": "నాకు",
            "neku": "నీకు",
            "vacha": "వచ్చా",
            "bagundi": "బాగుంది",
            "ekkada": "ఎక్కడ",
            "em": "ఏం",
            "cheshnav": "చేశ్నావ్",
            "unnava": "ఉన్నావా"
        }

    def _build_map(self):
        mapping = {}
        for char, data in TELUGU_VOWELS.items():
            mapping[char] = data['tenglish'].split(' / ')[0]
        for char, data in TELUGU_CONSONANTS.items():
            mapping[char] = data['tenglish'].split(' / ')[0]
        return mapping

    def to_telugu(self, text: str) -> str:
        """Simple conversion of Tenglish to Telugu (best effort)"""
        text = text.lower().strip()
        if text in self.common_mappings:
            return self.common_mappings[text]
        # Basic character-by-character logic (simplified)
        return text # Placeholder for complex logic

    def to_tenglish(self, telugu_text: str) -> str:
        """Convert Telugu script to Tenglish"""
        # Logic to iterate over characters and matras
        return telugu_text # Placeholder
