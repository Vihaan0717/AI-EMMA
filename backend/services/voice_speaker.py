import win32com.client
import pythoncom
import re
import os
import requests
import edge_tts
import asyncio
from core.logger import get_logger

logger = get_logger("VoiceSpeaker")

# ---------------------------------------------------------------------------
# Lazy-load the StreamingVoicePipeline (preferred) or HumanVoicePipeline
# ---------------------------------------------------------------------------
_human_pipeline = None
_streaming_pipeline = None

def _get_streaming_pipeline():
    global _streaming_pipeline
    if _streaming_pipeline is None:
        try:
            from voice.streaming_pipeline import StreamingVoicePipeline
            _streaming_pipeline = StreamingVoicePipeline()
            logger.info("[OK] StreamingVoicePipeline loaded.")
        except Exception as e:
            logger.warning(f"StreamingVoicePipeline unavailable ({e}).")
            _streaming_pipeline = False
    return _streaming_pipeline if _streaming_pipeline else None

def _get_pipeline():
    global _human_pipeline
    if _human_pipeline is None:
        try:
            from voice.human_voice_pipeline import HumanVoicePipeline
            _human_pipeline = HumanVoicePipeline()
            logger.info("[OK] HumanVoicePipeline loaded as primary TTS.")
        except Exception as e:
            logger.warning(f"HumanVoicePipeline unavailable ({e}). Using legacy SAPI5.")
            _human_pipeline = False  # Sentinel: don't try again
    return _human_pipeline if _human_pipeline else None

class VoiceSpeaker:
    """JARVIS's ultra-stable direct Windows vocal cords."""
    
    def __init__(self):
        pythoncom.CoInitialize()
        self.engine = win32com.client.Dispatch("SAPI.SpVoice")
        self.engine.Rate = -2 
        self.engine.Volume = 100
        # For coordination with VoiceListener
        self.active_speaking = False
        # Ensure the audio directory exists for the web server
        self.audio_dir = os.path.join(os.getcwd(), "avatar", "audio")
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
        logger.info(f"Voice Speaker initialized. Audio path: {self.audio_dir}")

    def speak(self, text: str, emotion: str = "neutral", force_local: bool = False, pose: str = None, agent_id: str = None):
        """
        JARVIS voice output — now powered by the HumanVoicePipeline.

        Priority chain:
          1. HumanVoicePipeline (Kokoro-82M or Edge-TTS with emotion + breath)
          2. Legacy SAPI5 (absolute last resort — no kokoro, no edge-tts)
        """
        self.active_speaking = True

        try:
            if pose:
                try:
                    from core.avatar_server import avatar_server_instance
                    avatar_server_instance.trigger_animation(pose)
                except Exception:
                    pass

            logger.info(f"JARVIS Speaking [{emotion}]: '{text[:80].strip()}...'")

            # ── ATTEMPT 1: HumanVoicePipeline ──────────────────────────────
            pipeline = _get_pipeline()
            if pipeline and not force_local:
                def _on_first():
                    """Mark speaking as active when first chunk plays."""
                    self.active_speaking = True

                pipeline.speak(text, emotion=emotion, on_first_chunk=_on_first, agent_id=agent_id)

                # Block until Kokoro finishes (non-blocking pipeline, so we poll)
                import time
                poll_start = time.time()
                while pipeline.active_speaking and self.active_speaking:
                    if time.time() - poll_start > 120:   # 2-min safety cap
                        break
                    time.sleep(0.05)
                return

            # ── ATTEMPT 2: Legacy SAPI5 (force_local or pipeline failed) ───
            logger.info("Using legacy SAPI5 fallback.")
            try:
                from core.avatar_server import avatar_server_instance
                avatar_server_instance.trigger_animation("TALKING")
                avatar_server_instance.send_ai_response(
                    re.sub(r'[*_#`~]', '', text).encode('ascii','ignore').decode('ascii'),
                    emotion=emotion
                )
            except Exception:
                pass

            clean_text = re.sub(r'[*_#`~]', '', text)
            clean_text = clean_text.encode('ascii', 'ignore').decode('ascii')
            self.engine.Speak(clean_text, 1)   # flag=1: async

            import time
            while self.engine.Status.RunningState != 1 and self.active_speaking:
                time.sleep(0.1)

            try:
                from core.avatar_server import avatar_server_instance
                avatar_server_instance.trigger_animation("STOP_TALKING")
            except Exception:
                pass

        finally:
            self.active_speaking = False

    async def speak_streaming(self, token_stream, emotion: str = "neutral", agent_id: str = None):
        """
        Stream tokens from the LLM directly to the voice engine.
        Speech starts after the first sentence is accumulated (~2s).
        Falls back to blocking speak() if streaming pipeline is unavailable.
        """
        sp = _get_streaming_pipeline()
        if sp:
            await sp.speak_streaming(token_stream, emotion=emotion, agent_id=agent_id)
        else:
            # Fallback: collect all tokens, then speak
            full_text = ""
            async for token in token_stream:
                full_text += token
            if full_text.strip():
                self.speak(full_text, emotion=emotion, agent_id=agent_id)

    def stop(self):
        """Interrupts any ongoing speech immediately."""
        logger.info("Interrupting JARVIS speech...")
        self.active_speaking = False
        try:
            # Purge the SAPI buffer
            self.engine.Speak("", 3) 
        except Exception as e:
            logger.error(f"Failed to stop speech: {e}")

    async def generate_voice_file(self, text: str, voice: str = None, output_path: str = None) -> str:
        """Generates an mp3 file from text using edge-tts."""
        try:
            # Default to Telugu if text has Telugu characters
            if not voice:
                if any('\u0c00' <= char <= '\u0c7f' for char in text):
                    voice = "te-IN-ShrutiNeural" # High-quality Telugu
                else:
                    voice = "en-US-AnaNeural" # Cute English fallback

            if not output_path:
                output_path = os.path.join(self.audio_dir, f"voice_{int(time.time())}.mp3")

            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate voice file: {e}")
            return None

# Test the vocal cords directly!
if __name__ == "__main__":
    mouth = VoiceSpeaker()
    print("\n[TEST] Testing Audio Output...\n")
    mouth.speak("Hello Boss. My direct Windows vocal systems are fully operational.")
