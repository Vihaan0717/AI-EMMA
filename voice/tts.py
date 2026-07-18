import asyncio
import edge_tts
import logging
import os

logger = logging.getLogger("jarvis.voice.tts")

class TTSEngine:
    """
    High-quality free TTS using edge-tts.
    Supports English and Telugu.
    """
    
    VOICES = {
        "english": "en-US-GuyNeural",
        "telugu": "te-IN-MohanNeural",
        "casual": "en-GB-RyanNeural"
    }

    def _phonetic_preprocess(self, text: str, voice_key: str) -> str:
        """Preprocesses Tenglish/Dakhni words for better phonetic pronunciation."""
        if voice_key != "telugu":
            return text
            
        tenglish_map = {
            r"\bnuvvu\b": "నువ్వు",
            r"\bela\b": "ఎలా",
            r"\bunnav\b": "ఉన్నావ్",
            r"\bunnaru\b": "ఉన్నారు",
            r"\bbest\b": "బెస్ట్",
            r"\bfriend\b": "ఫ్రెండ్",
            r"\bboss\b": "బాస్",
            r"\bnamaste\b": "నమస్తే",
            r"\bnamaskaram\b": "నమస్కారం",
            r"\bcheppu\b": "చెప్పు",
            r"\bchesav\b": "చేసావ్",
            r"\bchestunnav\b": "చేస్తున్నావ్",
            r"\bchala\b": "చాలా",
            r"\bbavundi\b": "బావుంది",
            r"\bbagundi\b": "బాగుంది",
            r"\bavunu\b": "అవును",
            r"\bledu\b": "లేదు",
            r"\bsare\b": "సరే",
            r"\benti\b": "ఏంటి",
            r"\bem\b": "ఏం",
            r"\bikkada\b": "ఇక్కడ",
            r"\bekkada\b": "ఎక్కడ",
            r"\beppudu\b": "ఎప్పుడు",
            r"\bevaru\b": "ఎవరు",
            r"\benduku\b": "ఎందుకు",
            r"\bwork\b": "వర్క్",
            r"\bcode\b": "కోడ్",
            r"\berror\b": "ఎర్రర్",
            r"\bproblem\b": "ప్రాబ్లం",
            r"\bkani\b": "కానీ",
            r"\bchudu\b": "చూడు",
            r"\bchey\b": "చెయ్"
        }
        
        import re
        processed = text
        for pat, repl in tenglish_map.items():
            processed = re.sub(pat, repl, processed, flags=re.IGNORECASE)
        return processed

    async def speak(self, text: str, voice_key: str = "telugu", output_file: str = "temp/speech.mp3"):
        """Synthesize text to speech."""
        voice = self.VOICES.get(voice_key, self.VOICES["english"])
        
        # Preprocess text to pronounce Tenglish naturally
        processed_text = self._phonetic_preprocess(text, voice_key)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        logger.info(f"Synthesizing [{voice}]: {processed_text[:50]}...")
        
        try:
            communicate = edge_tts.Communicate(processed_text, voice)
            await communicate.save(output_file)
            logger.info(f"Saved to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"TTS Failed: {e}")
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = TTSEngine()
    asyncio.run(engine.speak("Namaste Boss, nuvvu ela unnav?", voice_key="telugu"))
