import speech_recognition as sr
import time
import io
import logging
import numpy as np
from faster_whisper import WhisperModel
from core.logger import get_logger
from config.system_config import JarvisConfig
from services.music_service import music_service

logger = get_logger("VoiceListener")

class VoiceListener:
    """
    JARVIS audio intake system with Barge-In capability.
    Ears remain open even when JARVIS is talking or music is playing.
    """

    def __init__(self, model_size="base"):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.2
        self.recognizer.energy_threshold = JarvisConfig.ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = True
        
        self._mic_ready = True
        self._mic_error_logged = False
        self._mic_checked = False

        # Initialize Faster Whisper
        logger.info(f"Loading Faster Whisper model ({model_size})...")
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        logger.info("Voice Listener initialized. Barge-In mode enabled.")

    def is_available(self) -> bool:
        if self._mic_checked: return self._mic_ready
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            count = p.get_device_count()
            p.terminate()
            self._mic_ready = count > 0
        except Exception:
            self._mic_ready = False
        self._mic_checked = True
        return self._mic_ready

    def listen(self, language_code: str = None, speaker=None):
        """Listen from microphone with Barge-In and Music Interruption."""
        if not self.is_available():
            time.sleep(1)
            return "", None

        try:
            mic = sr.Microphone()
        except Exception as e:
            logger.error(f"Microphone unavailable: {e}")
            return "", None

        with mic as source:
            # --- BARGE-IN PREP ---
            is_output_active = (speaker and speaker.active_speaking) or music_service.is_playing
            
            if is_output_active:
                logger.info("Barge-In active: Ducking audio and monitoring for speech...")
                music_service.duck(10) # Drop music to 10%
                # Use a higher threshold during playback to avoid self-triggering
                trigger_threshold = JarvisConfig.BARGE_IN_THRESHOLD 
            else:
                music_service.unduck() # Ensure full volume
                trigger_threshold = JarvisConfig.ENERGY_THRESHOLD

            print(f"\nJARVIS is listening... {'(Barge-In Enabled)' if is_output_active else ''}")
            
            try:
                # 1. Wait for speech with dynamic interruption
                # We use a short phrase_time_limit to detect "interruptions" quickly
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                
                # 2. If we got here, something was heard.
                # Check if it was a barge-in (user spoke while JARVIS was talking)
                if (speaker and speaker.active_speaking) or music_service.is_playing:
                    logger.info("Speech detected during playback! Interrupting...")
                    if speaker: speaker.stop()
                    music_service.interrupt()
                
                # Restore volume immediately
                music_service.unduck()

                # 3. Process with Faster Whisper
                print("Processing audio...")
                wav_data = io.BytesIO(audio.get_wav_data())
                target_lang = language_code.split('-')[0] if language_code else None
                segments, info = self.model.transcribe(wav_data, beam_size=5, language=target_lang)
                
                text = "".join([segment.text for segment in segments]).strip()
                detected_lang = info.language

                # Hallucination Filter: Ignore very short or repetitive garbage often caused by self-hearing
                if text and len(text) > 1:
                    # Check for common hallucinated phrases (e.g. "Thank you.", "Bye.", "Subtitle by...")
                    garbage = ["thank you", "bye", "subtitles", "watching", "subscribe"]
                    if any(g == text.lower().strip('.') for g in garbage):
                        logger.warning(f"Filtered hallucination: {text}")
                        return "", detected_lang
                        
                    logger.info(f"Detected {detected_lang}: {text}")
                    return text, detected_lang
                
                return "", detected_lang

            except sr.WaitTimeoutError:
                music_service.unduck()
                return "", None
            except Exception as e:
                music_service.unduck()
                logger.error(f"Microphone error: {e}")
                return "", None

# Test logic
if __name__ == "__main__":
    ears = VoiceListener()
    print(ears.listen())
