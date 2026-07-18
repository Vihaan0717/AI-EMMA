import os
import queue
import threading
import numpy as np
from faster_whisper import WhisperModel
from voice.correction_ledger import CorrectionLedger
import logging
from typing import Optional, Dict, Any, List, Callable

logger = logging.getLogger("nexus.audio_intelligence")

class AudioIntelligenceProcessor:
    """
    Local Audio Processing Pipeline for VoIP.
    Uses Faster-Whisper for real-time STT without external tokens.
    """
    def __init__(self, model_type="large-v3", device="auto", compute_type="int8_float16"):
        logger.info(f"Initializing Local ASR model ({model_type})...")
        self.model_type = model_type
        # Using large-v3 for maximum accuracy in Telugu/English Tenglish detection
        self.model = WhisperModel(model_type, device=device, compute_type=compute_type)
        self.ledger = CorrectionLedger()
        self.audio_queue = queue.Queue()
        self.is_running = False
        self._thread = None
        self._wake_word = "jarvis"
        self._is_listening = False
        self._on_wake_callback: Optional[Callable] = None

    def start(self):
        self.is_running = True
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()
        logger.info("Audio Intelligence Processor started.")

    def stop(self):
        self.is_running = False
        if self._thread:
            self._thread.join()

    def add_audio_chunk(self, chunk: bytes):
        """Adds raw audio bytes from the stream."""
        # Convert bytes to numpy float32
        audio_data = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
        self.audio_queue.put(audio_data)

    def _process_loop(self):
        while self.is_running:
            try:
                # Accumulate a bit of audio for better transcription context
                chunks = []
                # Wait for at least one chunk
                chunks.append(self.audio_queue.get(timeout=1))
                
                # Try to get more chunks if available immediately
                while not self.audio_queue.empty():
                    chunks.append(self.audio_queue.get_nowait())
                
                audio_buffer = np.concatenate(chunks)
                
                # Transcribe
                segments, info = self.model.transcribe(audio_buffer, language="te", beam_size=5)
                
                for segment in segments:
                    if segment.text.strip():
                        # Apply Correction Ledger
                        corrected_text = self.ledger.apply_stt_corrections(segment.text)
                        
                        logger.info(f"[STT] Detected ({info.language}): {corrected_text}")
                        # Here we would emit an event to the Message Bus or Brain
                        self._handle_transcript(corrected_text, info.language)
                        
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Audio processing error: {e}")

    def _handle_transcript(self, text: str, language: str):
        """Push transcript to the system brain."""
        # This will be linked to the Brain via MessageBus in the full implementation
        pass

if __name__ == "__main__":
    # Test stub
    processor = AudioIntelligenceProcessor()
    processor.start()
    # Mock some audio data...
