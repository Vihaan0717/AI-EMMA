# arion/language/free_translator.py

from typing import Optional


class FreeTranslator:
    """
    Free Translation - No API Keys!
    Uses deep-translator (Google Translate unofficial API)
    """

    def __init__(self):
        print("✅ [Translator] Free Translator Ready")

    def translate(self, text: str, source: str = 'auto', target: str = 'en') -> str:
        """Translate text using deep-translator"""
        if not text or not text.strip():
            return text

        try:
            from deep_translator import GoogleTranslator
            
            # Note: source='auto' is supported by deep-translator
            translated = GoogleTranslator(source=source, target=target).translate(text)
            return translated if translated else text
            
        except Exception as e:
            print(f"⚠️ [Translator] Error: {e}")
            return text

    def detect_language(self, text: str) -> str:
        """Basic script-based language detection"""
        import re
        # Telugu unicode range: \u0C00-\u0C7F
        if re.search(r'[\u0C00-\u0C7F]', text):
            return 'te'
        return 'en'

    def telugu_to_english(self, text: str) -> str:
        return self.translate(text, source='te', target='en')

    def english_to_telugu(self, text: str) -> str:
        return self.translate(text, source='en', target='te')
