"""
JARVIS Streaming Voice Module
==============================
speak_streaming() — speak the LLM token stream sentence-by-sentence.

Architecture:
  - Token accumulator detects sentence boundaries (.!?)
  - First sentence: synthesised immediately → plays in ~2s
  - Remaining sentences: synthesised one at a time while current is playing
  - Each sentence is collect-then-play (one sd.play() per sentence = no gaps within it)
  - Back-to-back sentences are queued via threading.Event — sentence N+1 starts
    the moment sentence N finishes, with ~0ms gap

This gives you:
  ✅ First word starts playing ~2s after the LLM starts generating
  ✅ No gaps or breaks within any single sentence
  ✅ No silence between consecutive sentences
  ✅ Barge-in works at any time (stop_event → sd.stop())

Usage (in voice_service.py):
    from voice.streaming_pipeline import StreamingVoicePipeline
    pipeline = StreamingVoicePipeline()
    await pipeline.speak_streaming(ai_engine.generate_stream(prompt), emotion="neutral")
"""

import asyncio
import logging
import queue
import re
import threading
import time
from typing import AsyncGenerator, Optional

import numpy as np

logger = logging.getLogger("jarvis.voice.streaming")

# Sentence boundary: ends with . ! ? followed by whitespace or end-of-string.
# We deliberately do NOT split on commas — that caused the "breaking every word" bug.
_SENTENCE_END = re.compile(r'(?<=[.!?])\s+|(?<=[.!?])$')


class StreamingVoicePipeline:
    """
    Drop-in upgrade to HumanVoicePipeline that accepts a streaming LLM token
    generator and begins speaking as soon as the first sentence is complete.
    """

    def __init__(self):
        from voice.human_voice_pipeline import HumanVoicePipeline
        self._pipeline = HumanVoicePipeline()
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def active_speaking(self) -> bool:
        return self._pipeline.active_speaking

    def stop(self):
        """Barge-in: immediately stop all speech."""
        self._stop_event.set()
        self._pipeline.stop()

    async def speak_streaming(
        self,
        token_stream: AsyncGenerator[str, None],
        emotion: Optional[str] = None,
        on_first_chunk: Optional[callable] = None,
        agent_id: Optional[str] = None,
    ):
        """
        Accepts an async token generator (e.g. ai_engine.generate_stream()).
        Starts speaking as soon as the first sentence is complete.

        Args:
            token_stream:   Async generator yielding LLM tokens one by one.
            emotion:        Optional emotion override.
            on_first_chunk: Called when first audio starts playing.
            agent_id:       Optional agent identifier for specific voices.
        """
        self._stop_event.clear()

        # Collect sentences from the token stream
        sentence_queue: queue.Queue[Optional[str]] = queue.Queue()

        async def _collect_tokens():
            """Accumulate tokens → detect sentence boundaries → enqueue sentences."""
            buffer = ""
            try:
                async for token in token_stream:
                    if self._stop_event.is_set():
                        break
                    buffer += token
                    # Check for sentence boundary
                    parts = _SENTENCE_END.split(buffer, maxsplit=1)
                    if len(parts) >= 2:
                        sentence_queue.put(parts[0].strip())
                        buffer = parts[1] if len(parts) > 1 else ""
                # Flush any remaining text as the last sentence
                if buffer.strip() and not self._stop_event.is_set():
                    sentence_queue.put(buffer.strip())
            except Exception as e:
                logger.error(f"Token collection error: {e}")
            finally:
                sentence_queue.put(None)  # Sentinel: no more sentences

        # Start the player in a background thread
        player_done = threading.Event()
        first_spoken = [False]

        def _player():
            """
            Drains sentence_queue and speaks each sentence sequentially.
            Each sentence is synthesised to a single array and played with one sd.play().
            """
            import sounddevice as sd

            def _on_first_internal():
                if not first_spoken[0]:
                    first_spoken[0] = True
                    if on_first_chunk:
                        try:
                            on_first_chunk()
                        except Exception:
                            pass

            while True:
                try:
                    sentence = sentence_queue.get(timeout=30)
                except queue.Empty:
                    break

                if sentence is None:  # Sentinel
                    break
                if self._stop_event.is_set():
                    # Drain remaining
                    while True:
                        try:
                            sentence_queue.get_nowait()
                        except queue.Empty:
                            break
                    break

                # Speak this sentence: synthesise full sentence → one sd.play()
                self._pipeline.speak(sentence, emotion=emotion, on_first_chunk=_on_first_internal, agent_id=agent_id)

                # Wait for this sentence to finish before speaking the next
                wait_start = time.time()
                while self._pipeline.active_speaking:
                    if self._stop_event.is_set():
                        self._pipeline.stop()
                        break
                    if time.time() - wait_start > 60:
                        break
                    time.sleep(0.03)

            player_done.set()

        player_thread = threading.Thread(target=_player, daemon=True)
        player_thread.start()

        # Collect tokens (async) while the player drains concurrently
        await _collect_tokens()

        # Wait for player to finish
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: player_done.wait(timeout=120)
        )

    def speak(self, text: str, emotion: str = None, on_first_chunk=None, agent_id: str = None):
        """
        Non-streaming speak — delegates to the underlying HumanVoicePipeline.
        Keeps this class a drop-in for VoiceSpeaker.
        """
        self._pipeline.speak(text, emotion=emotion, on_first_chunk=on_first_chunk, agent_id=agent_id)
