import os
import sys
import time
import logging
import threading
import asyncio
import numpy as np
import sounddevice as sd

# Ensure root paths are in PYTHONPATH
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from voice.whisper_listener import WhisperListener
from services.voice_speaker import VoiceSpeaker
from core.fleet.manager import fleet_manager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("VoiceAssistant")

class VoiceAssistantLoop:
    """
    Central loop managing real-time speech intake, processing via cognitive fleet,
    and voice playback. Protects against echo loops via thread locks.
    """
    def __init__(self):
        self._check_ollama()
        logger.info("Initializing voice assistant engines...")
        
        # Start Avatar Server
        try:
            from core.avatar_server import avatar_server_instance
            avatar_server_instance.start()
            logger.info("Avatar Server started.")
        except Exception as e:
            logger.error(f"Failed to start Avatar Server: {e}")

    def _check_ollama(self):
        import urllib.request
        import urllib.error
        import subprocess
        try:
            urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2)
        except urllib.error.URLError:
            logger.warning("Ollama is not running. Attempting to start Ollama in the background...")
            try:
                # Start ollama using subprocess
                if sys.platform == "win32":
                    subprocess.Popen("ollama serve", shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
                else:
                    subprocess.Popen(["ollama", "serve"], start_new_session=True)
                time.sleep(3) # Wait for it to boot up
            except Exception as e:
                logger.error(f"Failed to start Ollama automatically: {e}. Please start it manually.")

        
        # Audio Configuration
        self.fs = 16000  # Whisper expects 16kHz
        self.channels = 1
        self.block_duration = 1.0  # 1 second block read intervals
        self.blocksize = int(self.fs * self.block_duration)
        
        # Initialize Mouth (Speaker) and Ears (STT Listener)
        self.mouth = VoiceSpeaker()
        self.ears = WhisperListener(model_size="base", device="cpu", compute_type="int8")
        
        # Locks to prevent self-hearing / loops
        self.speaking_lock = threading.Lock()
        
        # Callback linkage
        self.ears.set_callback(self.on_transcript)

    def on_transcript(self, text: str, lang: str, audio_data: np.ndarray = None):
        """Fires when Whisper detects speech."""
        # 1. Ignore if speaker is actively playing (prevents echo loops)
        if self.speaking_lock.locked() or self.mouth.active_speaking:
            logger.info("Ignoring transcription: Speaker is currently speaking.")
            return

        # Double check to prevent blank transcription triggers
        clean_text = text.strip()
        if not clean_text or len(clean_text) < 2:
            return

        print(f"\n[Heard] ({lang}): {clean_text}")
        
        # Start response processing on a separate worker thread so we don't block audio queues
        threading.Thread(target=self.process_and_speak, args=(clean_text, lang), daemon=True).start()

    def process_and_speak(self, text: str, lang: str):
        """Sends transcription to FleetManager and speaks the result."""
        # Acquire speaking lock to suppress microphone processing
        with self.speaking_lock:
            try:
                print("[Thinking]...")
                # Map STT lang to Tenglish/Telugu or default English rules
                assistant_lang = "tenglish" if lang == "te" else "english"
                
                # Execute task inside fleet manager (Hank or lead agent will handle it)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    fleet_manager.execute_task(text, language=assistant_lang)
                )
                loop.close()
                
                response_text = result.get("response", "Nenu clear ga vinakapoya, malli cheptara?")
                print(f"[Response]: {response_text}")
                
                # Speak output
                # Determine voice key based on detected language
                voice_key = "telugu" if lang == "te" else "casual"
                self.mouth.speak(response_text, force_local=True)
                
            except Exception as e:
                logger.error(f"Error in processing voice query: {e}", exc_info=True)
                self.mouth.speak("Sorry, technical failure in my cognitive pipeline.", force_local=True)

    def run(self):
        """Starts stream and listening loop."""
        print("\n" + "="*50)
        print("[NEXUS-X VOICE ASSISTANT ONLINE]")
        print("Speak directly. Press Ctrl+C to exit.")
        print("="*50 + "\n")

        self.ears.start()

        def audio_callback(indata, frames, time_info, status):
            if status:
                logger.warning(f"Audio stream status issue: {status}")
            
            # If speaking, discard audio chunks to prevent audio buffer pollution
            if self.speaking_lock.locked() or self.mouth.active_speaking:
                return

            # Convert float32 [-1, 1] input stream values to int16 PCM
            audio_int16 = (indata * 32768).astype(np.int16)
            self.ears.add_audio_chunk(audio_int16.tobytes())

        try:
            with sd.InputStream(samplerate=self.fs, channels=self.channels, blocksize=self.blocksize, callback=audio_callback):
                while True:
                    sd.sleep(1000)
        except KeyboardInterrupt:
            print("\nShutting down voice loop...")
        except Exception as e:
            logger.error(f"Crash in audio device capture: {e}")
        finally:
            self.ears.stop()
            print("NEXUS-X Ears offline.")

if __name__ == "__main__":
    assistant = VoiceAssistantLoop()
    assistant.run()
