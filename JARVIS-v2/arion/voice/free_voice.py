# arion/voice/free_voice.py

import os
import time
import threading
import queue
import tempfile
from typing import Optional, Callable


class FreeVoice:
    """
    100% Free Voice System
    STT: OpenAI Whisper (Local)
    TTS: pyttsx3 (Offline)
    """

    def __init__(self):
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.whisper_model = None
        self.tts_engine = None
        
        # Load whisper in background to not block startup
        threading.Thread(target=self._load_models, daemon=True).start()
        print("✅ [Voice] Free Voice System Initializing...")

    def _load_models(self):
        """Lazy load heavy models"""
        try:
            import whisper
            import pyttsx3
            
            # Load TTS
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            print("✅ [Voice] TTS Engine Loaded")
            
            # Load Whisper (Base model is ~150MB)
            model_size = os.getenv('WHISPER_MODEL', 'base')
            self.whisper_model = whisper.load_model(model_size)
            print(f"✅ [Voice] Whisper ({model_size}) Loaded")
            
            # Start queue processor
            self._start_speech_thread()
            
        except Exception as e:
            print(f"❌ [Voice] Error loading models: {e}")

    def _start_speech_thread(self):
        def process():
            while True:
                text = self.speech_queue.get()
                if text:
                    self._speak_now(text)
                self.speech_queue.task_done()
        
        threading.Thread(target=process, daemon=True, name="VoiceProcessor").start()

    def speak(self, text: str):
        """Add text to speech queue"""
        if text:
            self.speech_queue.put(text)

    def _speak_now(self, text: str):
        self.is_speaking = True
        try:
            if self.tts_engine:
                # Clean text of emojis/markers for cleaner TTS
                import re
                clean_text = re.sub(r'[^\w\s.,?!]', '', text)
                self.tts_engine.say(clean_text)
                self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ [Voice] TTS Error: {e}")
        finally:
            self.is_speaking = False

    def listen_and_transcribe(self, duration: int = 5) -> str:
        """Capture audio and transcribe using local Whisper"""
        try:
            import sounddevice as sd
            import numpy as np
            
            if not self.whisper_model:
                return "Whisper model not loaded yet."
            
            fs = 16000 # Whisper expects 16kHz
            print(f"🎙️ [Voice] Listening for {duration}s...")
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()
            
            # Convert to float32
            audio = recording.flatten().astype(np.float32)
            
            # Transcribe
            result = self.whisper_model.transcribe(audio)
            return result.get('text', '').strip()
            
        except Exception as e:
            print(f"❌ [Voice] Rec error: {e}")
            return ""
