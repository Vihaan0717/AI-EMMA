import asyncio
import numpy as np
import logging
import time
from typing import Optional, List
from collections import deque
from core.message_bus import MessageBus, Channel
from voice.whisper_listener import WhisperListener
from voice.streaming_pipeline import StreamingVoicePipeline
from services.voice_speaker import VoiceSpeaker
from services.speaker_guardian import SpeakerGuardian
from services.music_service import music_service
from config.system_config import JarvisConfig

logger = logging.getLogger("VoiceService")

class VoiceService:
    """
    JARVIS Voice Integration Service.
    Connects the Whisper Listener (STT) and the Voice Speaker (TTS) to the Brain.
    Optimized with a production-grade Voice Activity Detection (VAD) buffer system
    to ensure ultra-low CPU usage and near-instant response times.
    """
    def __init__(self, brain, bus: MessageBus):
        self.brain = brain
        self.bus = bus
        # Primary: StreamingVoicePipeline (speaks first sentence in ~2s while LLM streams)
        # Fallback: Legacy VoiceSpeaker (SAPI5) if Kokoro unavailable
        try:
            self.speaker = StreamingVoicePipeline()
            logger.info("[VoiceService] StreamingVoicePipeline active.")
        except Exception as e:
            logger.warning(f"[VoiceService] Streaming pipeline failed ({e}), falling back to VoiceSpeaker.")
            self.speaker = VoiceSpeaker()
        self.loop = asyncio.get_event_loop()
        
        # Initialize Whisper
        self.listener = WhisperListener(model_size="base", device="cpu", compute_type="int8")
        self.listener.initial_prompt = "English and Telugu conversation. Namaste, JARVIS. Tenglish."
        
        self.guardian = SpeakerGuardian()
        self.is_running = False
        self._task = None

    async def start(self):
        """Starts the voice interaction loop."""
        self.is_running = True
        self.listener.set_callback(self._on_transcription)
        self.listener.start()
        
        # Audio capturing loop using sounddevice with our high-performance VAD buffer
        self._task = asyncio.create_task(self._audio_capture_loop())
        logger.info("[VoiceService] Active. Listening for commands...")

    async def stop(self):
        """Stops the voice service."""
        self.is_running = False
        self.listener.stop()
        if self._task:
            self._task.cancel()
        logger.info("Voice Service deactivated.")

    def _on_transcription(self, text: str, lang: str, audio_data: Optional[np.ndarray] = None):
        """Callback for when Whisper detects speech."""
        if not text.strip():
            return

        # --- POWERFUL BARGE-IN LOGIC ---
        is_jarvis_busy = self.speaker.active_speaking or music_service.is_playing
        
        if is_jarvis_busy:
            if len(text.strip()) < 3: 
                return
            
            # Filter common hallucinations
            garbage = ["thank you", "bye", "subtitles", "watching", "subscribe", "oh", "um", "uh"]
            if any(g == text.lower().strip('.') for g in garbage):
                return

            logger.info(f"Barge-In detected: User interrupted with '{text}'")
            self.speaker.stop()
            music_service.interrupt()
            music_service.unduck()

        # ── BIOMETRIC SECURITY ──────────────────────────────────────────
        if audio_data is not None:
            if not self.guardian.is_authorized(audio_data):
                logger.warning(f"Unauthorized voice detected: '{text}'. Access Denied.")
                return
        # ────────────────────────────────────────────────────────────────

        logger.info(f"🎙️ Voice Detected ({lang}): {text}")
        
        asyncio.run_coroutine_threadsafe(
            self._process_voice_command(text), 
            self.loop
        )

    async def _process_voice_command(self, text: str):
        """Processes the transcription through the brain and speaks back.

        If the brain exposes generate_stream(), we stream tokens directly to
        speak_streaming() so speech begins after the first sentence (~2 seconds).
        Otherwise we fall back to the blocking process_input() call.
        """
        try:
            # ── STREAMING PATH (preferred — lowest perceived latency) ─────
            if hasattr(self.brain, 'ai') and hasattr(self.brain.ai, 'generate_stream') \
                    and isinstance(self.speaker, StreamingVoicePipeline):
                # Build the prompt the same way the pipeline does
                prompt = text
                token_stream = self.brain.ai.generate_stream(prompt)
                await self.speaker.speak_streaming(token_stream)
                return

            # ── BLOCKING PATH (fallback) ──────────────────────────────────
            result = await self.brain.process_input(text, source="voice")
            response = result.get("response", "")
            if response:
                if isinstance(self.speaker, StreamingVoicePipeline):
                    self.speaker.speak(response)
                else:
                    self.speaker.speak(response)
        except Exception as e:
            logger.error(f"Voice processing error: {e}")

    async def _audio_capture_loop(self):
        """Captures audio from the mic and processes it through a sliding-window VAD buffer."""
        import sounddevice as sd
        
        fs = 16000
        channels = 1
        block_duration = 0.2  # 200ms chunks for rapid energy analysis
        blocksize = int(fs * block_duration)

        # Production-grade VAD State Variables
        vad_state = "IDLE"  # IDLE | SPEAKING
        pre_buffer = deque(maxlen=6)  # Keep last 1.2s of audio to prevent clipping the beginning
        speaking_chunks = []
        silence_accumulated = 0.0
        
        # Audio energy settings mapped from config
        base_threshold = JarvisConfig.ENERGY_THRESHOLD / 20000.0  # e.g., 400 -> 0.02
        barge_in_threshold = JarvisConfig.BARGE_IN_THRESHOLD / 20000.0  # e.g., 800 -> 0.04

        def audio_callback(indata, frames, time_info, status):
            nonlocal vad_state, speaking_chunks, silence_accumulated
            
            if status:
                logger.warning(f"Audio status: {status}")

            # Calculate RMS energy of current 200ms chunk
            rms = np.sqrt(np.mean(indata**2))
            
            # Determine threshold based on system activity (TTS speaking or music playing)
            is_active = self.speaker.active_speaking or music_service.is_playing
            current_threshold = barge_in_threshold if is_active else base_threshold

            # Ducking control
            if is_active and rms > current_threshold:
                music_service.duck(15)
            elif not is_active:
                music_service.unduck()

            # --- VAD STATE MACHINE ---
            if vad_state == "IDLE":
                if rms > current_threshold:
                    # Speech detected! Trigger transition
                    vad_state = "SPEAKING"
                    silence_accumulated = 0.0
                    
                    # Convert pre-buffer to list and start recording speech
                    speaking_chunks = list(pre_buffer)
                    speaking_chunks.append(indata.copy())
                    logger.debug("VAD: Speech started...")
                else:
                    # Keep rolling the pre-buffer
                    pre_buffer.append(indata.copy())
                    
            elif vad_state == "SPEAKING":
                speaking_chunks.append(indata.copy())
                
                if rms < current_threshold:
                    silence_accumulated += block_duration
                    # If user is silent for 1.2 seconds, finalize the sentence
                    if silence_accumulated >= 1.2:
                        vad_state = "IDLE"
                        logger.debug("VAD: Speech ended. Dispatching block to Whisper...")
                        
                        # Concatenate and compile the compiled audio array
                        full_audio = np.concatenate(speaking_chunks)
                        # Convert to int16 bytes for WhisperListener
                        audio_int16 = (full_audio * 32768).astype(np.int16)
                        self.listener.add_audio_chunk(audio_int16.tobytes())
                        
                        speaking_chunks = []
                else:
                    # Reset silence tracker since there is ongoing sound
                    silence_accumulated = 0.0

        try:
            with sd.InputStream(samplerate=fs, channels=channels, blocksize=blocksize, callback=audio_callback):
                while self.is_running:
                    await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Microphone capture error: {e}")
            self.is_running = False

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    
    async def test():
        from core.message_bus import MessageBus
        bus = MessageBus()
        await bus.start()
        class MockBrain:
            async def process_input(self, text, source):
                return {"response": f"I heard you say: {text}"}
        
        voice = VoiceService(MockBrain(), bus)
        await voice.start()
        await asyncio.sleep(60)
    
    asyncio.run(test())
