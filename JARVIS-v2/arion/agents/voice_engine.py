import asyncio
import os
import threading
import queue
import time
import numpy as np
import traceback
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

class VoiceEngine(BaseAgent):
    def __init__(self, model_size="base"):
        super().__init__("VoiceEngine", [Channel.VOICE])
        self.state = "WARMING_UP" 
        self.model_size = model_size
        self.voice = "en-US-AndrewNeural" 
        self.model = None
        self.recognizer = None
        self.mic = None
        self.pygame = None
        self.inference_paused = False

    async def run_loop(self):
        # 1. Start heavy initialization in background loop
        print(f"[VoiceEngine] Loading heavy AI models and hardware ({self.model_size})...", flush=True)
        def _load_heavy_models():
            try:
                # Deferred heavy imports stored on self for instance-wide visibility
                import speech_recognition as sr
                import edge_tts
                import pygame
                self.sr = sr
                self.edge_tts = edge_tts
                self.pygame = pygame
                
                from faster_whisper import WhisperModel
                
                print("[VoiceEngine] Libraries loaded. Initializing model...", flush=True)
                self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
                self.recognizer = self.sr.Recognizer()
                self.mic = self.sr.Microphone()
                
                # Noise Suppression Setup
                self.recognizer.energy_threshold = 1000 
                self.recognizer.dynamic_energy_threshold = False
                
                # Audio Init
                try:
                    self.pygame.mixer.quit()
                    self.pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
                except:
                    self.pygame.mixer.init()
                
                return True
            except Exception as e:
                print(f"[VoiceEngine] Initialization Error: {e}", flush=True)
                traceback.print_exc()
                return False

        success = await asyncio.to_thread(_load_heavy_models)
        if success:
            self.state = "IDLE"
            print("[VoiceEngine] High-Fidelity 44.1kHz Audio & Noise Suppression Ready.", flush=True)
        else:
            self.state = "ERROR"
            print("[VoiceEngine] Voice system failed to initialize.", flush=True)
        
        while self.running:
            try:
                # 1. Check for incoming bus messages (e.g. "speak" commands)
                msg = await self.get_next_message(timeout=0.05)
                if msg:
                    await self.handle_message(msg)

                # 2. Non-blocking mic listen (only when idle)
                if self.state == "IDLE" and self.mic and self.recognizer:
                    await self._listen_loop()
                elif self.state != "IDLE":
                    await asyncio.sleep(0.2)
            except Exception as e:
                if "timeout" not in str(e).lower():
                    print(f"[VoiceEngine] Loop Error: {e}", flush=True)
                await asyncio.sleep(0.5)

    async def _listen_loop(self):
        """Monitors microphone in a BACKGROUND THREAD so the event loop stays free."""
        def _sync_listen():
            """Runs in a thread — safe to block here."""
            try:
                with self.mic as source:
                    return self.recognizer.listen(source, timeout=2.0, phrase_time_limit=10.0)
            except Exception:
                # WaitTimeoutError is normal when nobody is speaking
                return None

        # Run the blocking listen() in a thread so we don't starve asyncio
        audio = await asyncio.to_thread(_sync_listen)
        if audio is None:
            return  # Timeout — nobody spoke, silently continue

        if self.inference_paused:
            # Low power mode: just detect volume, don't transcribe
            print("[VoiceEngine] Activity detected (Inference Paused).", flush=True)
            return

        self.state = "PROCESSING"
        try:
            wav_data = audio.get_wav_data()
            temp_wav = f"temp_voice_{int(time.time())}.wav"
            with open(temp_wav, "wb") as f:
                f.write(wav_data)

            segments, info = await asyncio.to_thread(
                lambda: self.model.transcribe(temp_wav, beam_size=5)
            )

            text = " ".join([segment.text for segment in segments]).strip()
            if os.path.exists(temp_wav): os.remove(temp_wav)

            # Ignore short dots or fragments often caused by noise
            if text and len(text) > 5 and "." not in text[0:3]:
                print(f"[VoiceEngine] I heard: \"{text}\"", flush=True)
                await self.send(
                    to_channel=Channel.ORCHESTRATOR,
                    action="process_input",
                    payload={"text": text, "source": "voice", "contact": "Owner (Voice)", "is_owner": True}
                )
            else:
                if text: print(f"[VoiceEngine] Ignored Noise: \"{text}\"", flush=True)
        except Exception as e:
            print(f"[VoiceEngine] Transcribe Error: {e}", flush=True)

        self.state = "IDLE"

    async def handle_message(self, message: Message):
        if message.action == "speak":
            text = message.payload.get("text", "")
            if text:
                await self._speak(text)
        elif message.action == "pause_inference":
            self.inference_paused = True
            print("[VoiceEngine] Inference PAUSED (Battery Saver). Noise only.")
        elif message.action == "resume_inference":
            self.inference_paused = False
            print("[VoiceEngine] Inference RESUMED.")

    async def _speak(self, text):
        if not self.pygame or not self.edge_tts:
             print("[VoiceEngine] Cannot speak: edge_tts or pygame not loaded yet.", flush=True)
             return

        self.state = "SPEAKING"
        print(f"[VoiceEngine] Speaking (High-Fidelity): {text}", flush=True)
        
        temp_file = "arion_voice.mp3"
        try:
            communicate = self.edge_tts.Communicate(text, self.voice)
            await communicate.save(temp_file)
            
            self.pygame.mixer.music.load(temp_file)
            self.pygame.mixer.music.play()
            while self.pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
            self.pygame.mixer.music.unload()
            if os.path.exists(temp_file): os.remove(temp_file)
        except Exception as e:
            print(f"[VoiceEngine] TTS Error: {e}", flush=True)
        
        await asyncio.sleep(0.3) # Faster recovery
        self.state = "IDLE"

    def __del__(self):
        try: 
            if self.pygame: self.pygame.mixer.quit()
        except: pass
