"""
JARVIS Human Voice Pipeline
============================
Single entry point that orchestrates the full ultra-human voice chain:

    Text → EmotionClassifier → HumanPreprocessor → KokoroEngine → AudioHumanizer → Speaker

Usage (drop-in replacement anywhere VoiceSpeaker is used):
    pipeline = HumanVoicePipeline()
    pipeline.speak("Hello, Boss!")

Supports:
  - Emotion override:  pipeline.speak("...", emotion="angry")
  - Barge-in:         pipeline.stop()
  - Avatar sync:       Passes emotion + talking state to avatar server
"""

import logging
import time
from typing import Optional

from voice.emotion_classifier import classify, EmotionResult
from voice.human_preprocessor import preprocess
from voice.kokoro_engine import KokoroTTSEngine, EdgeTTSFallback

logger = logging.getLogger("jarvis.voice.pipeline")


class HumanVoicePipeline:
    """
    Top-level voice pipeline. All JARVIS speech goes through here.
    """

    def __init__(self):
        logger.info("Initialising HumanVoicePipeline...")

        # Primary engine
        self._kokoro = KokoroTTSEngine()

        # Fallback (always available — only requires edge-tts)
        self._fallback = EdgeTTSFallback()

        if self._kokoro.is_available:
            logger.info("[Voice] Pipeline ready -- PRIMARY: Kokoro-82M (GPU)")
            # Warm up the ONNX runtime in background so first real response is instant
            import threading
            threading.Thread(target=self._warmup, daemon=True).start()
        else:
            logger.warning("[Voice] Pipeline ready -- PRIMARY: Edge-TTS (Kokoro not found)")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def active_speaking(self) -> bool:
        """Returns True while audio is being played."""
        return self._kokoro.active_speaking or self._fallback.active_speaking

    def speak(
        self,
        text: str,
        emotion: Optional[str] = None,
        on_first_chunk: Optional[callable] = None,
        agent_id: Optional[str] = None,
    ):
        """
        Speak with full human-like quality.

        Args:
            text:           Raw response text from LLM.
            emotion:        Optional emotion override (e.g. "angry", "sad").
                            If None, auto-detected from text content.
            on_first_chunk: Called when first audio starts playing (for avatar sync).
            agent_id:       Optional agent ID to override voice assignments.
        """
        if not text or not text.strip():
            return

        t_start = time.perf_counter()

        # 1. Classify emotion
        emotion_result: EmotionResult = classify(text, override=emotion)
        logger.info(
            f"[Emotion] [{emotion_result.label}] "
            f"intensity={emotion_result.intensity:.2f} "
            f"voice={emotion_result.voice_id} rate={emotion_result.rate:.2f}"
        )

        # 2. Preprocess text (inject breath markers, starters, etc.)
        processed = preprocess(text, emotion_result)
        logger.debug(f"Preprocessed: {processed[:120]}...")

        # 3. Sync avatar animation if available
        self._notify_avatar_start(emotion_result.label)

        # 4. Speak via Kokoro (or fallback)
        def _on_first():
            ms = (time.perf_counter() - t_start) * 1000
            logger.info(f"[Voice] First audio chunk in {ms:.1f} ms")
            if on_first_chunk:
                on_first_chunk()

        if self._kokoro.is_available:
            self._kokoro.speak(
                processed,
                emotion_label=emotion_result.label,
                rate=emotion_result.rate,
                on_first_chunk=_on_first,
                agent_id=agent_id,
            )
        else:
            self._fallback.speak(
                processed,
                emotion_label=emotion_result.label,
                rate=emotion_result.rate,
                on_first_chunk=_on_first,
            )

    def stop(self):
        """Immediately interrupt any ongoing speech (barge-in support)."""
        logger.info("[Voice] Barge-in: stopping speech.")
        self._kokoro.stop()
        self._fallback.stop()
        self._notify_avatar_stop()

    def _warmup(self):
        """Silent first synthesis to compile ONNX graph and warm phonemiser."""
        try:
            import numpy as np
            import sounddevice as sd
            logger.info("[Voice] Warming up Kokoro ONNX runtime...")
            # Synthesise a short silent-ish phrase — we discard the audio
            if self._kokoro._kokoro and self._kokoro._kokoro_api == "onnx":
                self._kokoro._kokoro.create(
                    "Ready.", voice="af_heart", speed=1.0, lang="en-us"
                )
            logger.info("[Voice] Warmup complete — first response will be instant.")
        except Exception as e:
            logger.debug(f"Warmup skipped: {e}")

    # ------------------------------------------------------------------
    # Avatar integration helpers
    # ------------------------------------------------------------------

    def _notify_avatar_start(self, emotion: str):
        try:
            from core.avatar_server import avatar_server_instance
            avatar_server_instance.trigger_animation("TALKING")
            # Map emotion to avatar expression
            _AVATAR_EMOTION_MAP = {
                "happy":      "happy",
                "excited":    "happy",
                "sad":        "sad",
                "depressed":  "sad",
                "angry":      "angry",
                "laugh":      "happy",
                "thoughtful": "neutral",
                "neutral":    "neutral",
            }
            avatar_emotion = _AVATAR_EMOTION_MAP.get(emotion, "neutral")
            avatar_server_instance.send_ai_response("", emotion=avatar_emotion)
        except Exception:
            pass  # Avatar not connected — silently skip

    def _notify_avatar_stop(self):
        try:
            from core.avatar_server import avatar_server_instance
            avatar_server_instance.trigger_animation("STOP_TALKING")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import time
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    )

    pipeline = HumanVoicePipeline()

    demo_lines = [
        ("Okay so... I've been thinking about this for a while now, and I honestly think we can do it!", None),
        ("I'm really sorry. I failed you on that task, and I feel terrible about it.", None),
        ("Haha! That is honestly the funniest thing I've heard all week. I wasn't ready for that at all.", None),
        ("Listen. I am not going to tolerate this kind of mistake again. It needs to stop, now.", None),
        ("Hmm. That's an interesting question. Let me think through the implications here...", None),
    ]

    for line, ovr in demo_lines:
        print(f"\n▶ Speaking: {line[:70]}...")
        pipeline.speak(line, emotion=ovr)
        # Wait for speech to complete
        time.sleep(0.3)
        while pipeline.active_speaking:
            time.sleep(0.1)
        time.sleep(0.5)

    print("\n✅ All voice tests complete.")
