import os
import re
import queue
import threading
import numpy as np
import logging
from faster_whisper import WhisperModel
from typing import Optional, Callable

logger = logging.getLogger("jarvis.voice.whisper")

class WhisperListener:
    """
    High-performance local STT using faster-whisper.
    Optimized for Telugu/English (Tenglish) detection.
    """
    def __init__(
        self, 
        model_size: str = "medium", # "large-v3" is best but heavy
        device: str = "auto", 
        compute_type: str = "int8_float16"
    ):
        logger.info(f"Initializing Faster-Whisper ({model_size})...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.audio_queue = queue.Queue()
        self.is_running = False
        self._thread = None
        self._callback: Optional[Callable] = None
        self._interrupt_callback: Optional[Callable] = None
        
        # Audio threshold for VAD barge-in
        self.energy_threshold = 0.05
        self.is_system_speaking = False

    def set_callback(self, callback: Callable):
        """Callback function for finished transcripts: callback(text, language)"""
        self._callback = callback

    def set_interrupt_callback(self, callback: Callable):
        """Callback fired immediately when loud speech is detected (Barge-in)"""
        self._interrupt_callback = callback
        
    def set_system_speaking(self, is_speaking: bool):
        """Tell the listener if the system is currently outputting audio to prevent self-interruption."""
        self.is_system_speaking = is_speaking

    def start(self):
        self.is_running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        logger.info("Whisper Listener active.")

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join()

    def add_audio_chunk(self, chunk: bytes):
        """Accepts raw 16-bit PCM audio chunks. Computes energy for barge-in."""
        audio_data = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Calculate RMS energy for VAD barge-in
        if len(audio_data) > 0:
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Dynamic thresholding: if system is speaking, we require a much louder sound to interrupt (ducking)
            current_threshold = self.energy_threshold * 2.5 if self.is_system_speaking else self.energy_threshold
            
            if rms > current_threshold:
                if self._interrupt_callback and self.is_system_speaking:
                    logger.info(f"[VAD] Loud spike detected (RMS: {rms:.4f} > {current_threshold:.4f}). Triggering barge-in!")
                    self._interrupt_callback()
                    # Reset speaking state to avoid rapid-fire interrupts
                    self.is_system_speaking = False

        self.audio_queue.put(audio_data)

    def _process_loop(self):
        while self.is_running:
            try:
                # Wait for audio to accumulate
                chunks = [self.audio_queue.get(timeout=1)]
                while not self.audio_queue.empty():
                    chunks.append(self.audio_queue.get_nowait())
                
                audio_buffer = np.concatenate(chunks)
                
                # Transcribe with VAD filter to ignore silence
                segments, info = self.model.transcribe(
                    audio_buffer, 
                    language=None, # Auto-detect for Tenglish
                    beam_size=10,
                    best_of=5,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=500),
                    initial_prompt="Jarvis, cheppu, enti sangati? How are you? I am fine. Namaste. Telugu English Tenglish mixture.",
                    condition_on_previous_text=False
                )
                
                # Store the audio buffer for verification
                transcription_audio = audio_buffer.copy()
                
                for segment in segments:
                    if segment.text.strip():
                        text = segment.text.strip()
                        
                        # ── LANGUAGE HALLUCINATION FILTER ────────────────────
                        detected_lang = info.language
                        if detected_lang not in ["en", "te"] and info.language_probability < 0.9:
                            if bool(re.match(r'^[a-zA-Z0-9\s\.,!\?]+$', text)):
                                detected_lang = "en"
                        # ──────────────────────────────────────────────────────
                        
                        # ── HALLUCINATION & SELF-HEARING FILTER ───────────────────
                        blacklist = [
                            "thank you", "thanks for watching", "subscribe", "bye", 
                            "i'll see you", "next video", "watching this", "youtube",
                            "um", "uh", "oh", "okay", "...", "..", "."
                        ]
                        text_lower = text.lower().strip('.!?, ')
                        if text_lower in blacklist or len(text_lower) < 2:
                            continue # Ignore hallucination
                        # ──────────────────────────────────────────────────────────
                        
                        logger.info(f"[Whisper] {detected_lang}: {text}")
                        if self._callback:
                            # Return text, lang, and the audio buffer used for this transcription
                            self._callback(text, detected_lang, transcription_audio)
                            
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Whisper processing error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    listener = WhisperListener()
    # In a real run, this would be fed by a sounddevice stream
    print("Whisper Listener Ready.")
