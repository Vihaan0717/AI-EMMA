import re
import logging

logger = logging.getLogger("nexus.voice.ledger")

class CorrectionLedger:
    """
    Standardizes Romanized Telugu and applies phonetic overrides 
    to fix common AI mispronunciations of 'soft' consonants.
    """
    def __init__(self):
        # Rules for STT (Standardizing transcribed text)
        self.stt_normalization = {
            r"\bcheppandi\b": "cheppandi", # standardizing common variants
            r"\beppudu\b": "eppudu",
            r"\bekkada\b": "ekkada",
            r"\benduku\b": "enduku",
            r"\benti\b": "enti",
        }
        
        # Phonetic overrides for TTS (Making it sound human)
        # e.g., 'soft' consonants like 'dh', 'th', 'sh'
        self.tts_phonetic_overrides = {
            "unnav": "un-naav",
            "unnaru": "un-naaru",
            "ela": "yela",
            "enti": "yenti",
            "nanna": "nan-na",
            "amma": "am-ma",
            "kaiku": "kai-koo",
            "hau": "how",
        }

    def apply_stt_corrections(self, text: str) -> str:
        """Fix common mis-transcriptions or variant spellings."""
        normalized = text.lower()
        for pattern, replacement in self.stt_normalization.items():
            normalized = re.sub(pattern, replacement, normalized)
        return normalized

    def apply_tts_phonetic_overrides(self, text: str) -> str:
        """Modify text to guide TTS engine for natural pronunciation."""
        # This is especially useful for Kokoro or MeloTTS
        # where specific phonetic spellings produce better results.
        words = text.split()
        overridden_words = []
        for word in words:
            # Strip punctuation for lookup
            clean_word = re.sub(r'[^\w]', '', word).lower()
            if clean_word in self.tts_phonetic_overrides:
                override = self.tts_phonetic_overrides[clean_word]
                # Re-add punctuation if it was there
                if word.endswith('?'): override += '?'
                elif word.endswith('.'): override += '.'
                elif word.endswith(','): override += ','
                overridden_words.append(override)
            else:
                overridden_words.append(word)
        
        return " ".join(overridden_words)

    def learn_correction(self, original: str, corrected: str):
        """Dynamically add a new correction rule."""
        # Future: Persist this to data/telugu_dna.json
        self.tts_phonetic_overrides[original.lower()] = corrected.lower()
        logger.info(f"Ledger learned new phonetic override: {original} -> {corrected}")
