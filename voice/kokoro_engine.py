"""
JARVIS Kokoro TTS Engine
==========================
Wraps Kokoro-82M ONNX with:
  - Emotion-driven voice ID and rate selection
  - Collect-then-play: full response synthesised to ONE array, played with ONE sd.play()
    → physically impossible to have gaps, breaks, or chunking between words/sentences
  - Barge-in support via sd.stop()
  - Graceful fallback to Edge-TTS if Kokoro is not installed

Usage:
    engine = KokoroTTSEngine()
    engine.speak("Hello, how are you today?", emotion_label="happy")

speak() is non-blocking — audio plays in a background thread.
"""

import logging
import os
import re
import threading
import time
from typing import Optional

import numpy as np

from voice.audio_humanizer import humanize, resolve_tokens, SAMPLE_RATE

logger = logging.getLogger("jarvis.voice.kokoro")
# Suppress noisy phonemizer warnings about word count mismatches
logging.getLogger("phonemizer").setLevel(logging.ERROR)

# ---------------------------------------------------------------------------
# Voice config – maps emotion labels to Kokoro voice IDs
# ---------------------------------------------------------------------------
_VOICE_MAP: dict[str, str] = {
    "neutral":    "af_heart",
    "happy":      "af_bella",
    "excited":    "af_bella",
    "sad":        "am_adam",
    "depressed":  "am_adam",
    "angry":      "am_michael",
    "thoughtful": "af_heart",
    "laugh":      "af_bella",
}

_AGENT_VOICE_MAP: dict[str, str] = {
    "jarvis_core": "am_adam", # Standard default JARVIS Kokoro male voice
    "psyche_agent": "clone:Voicesamp/female_ref.wav",
    "atlas_agent": "clone:Voicesamp/audio [vocals].mp3",
    "hank_agent": "clone:Voicesamp/YTDown_YouTube_ANIME-vs-VOICE-ACTORS-Best-Iconic-Moment_Media_AswBfKEgDu8_009_128k.mp3",
    "vision_agent": "am_michael"
}

_DEFAULT_VOICE = "af_heart"

# Regex to strip our custom human-sound tokens before they reach Kokoro's phonemiser
_TOKEN_STRIP = re.compile(r'\[(?:breath|sigh|exhale|hmm|laugh|pause:[^\]]+)\]')


# ---------------------------------------------------------------------------
# Kokoro Engine
# ---------------------------------------------------------------------------

class KokoroTTSEngine:
    """
    Primary ultra-human TTS engine powered by Kokoro-82M ONNX.

    Architecture: collect-then-play
      1. Synthesise the ENTIRE response into one numpy array (breath sounds + TTS).
      2. Play it with a single sd.play() call.
      → One hardware open, one hardware close, zero internal gaps.
    """

    def __init__(self):
        self._kokoro = None
        self._kokoro_api = None
        self._active = False
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._load_kokoro()

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def _load_kokoro(self):
        """
        Try to load Kokoro in priority order:
          1. kokoro-onnx  — Python 3.13 compatible, no spacy/misaki needed
          2. KPipeline    — kokoro >= 0.9.x PyTorch API
          3. generate()   — kokoro 0.7.x legacy API
        """
        self._kokoro = None
        self._kokoro_api = None

        # Option 1: kokoro-onnx (Python 3.13 safe) ───────────────────────
        try:
            from kokoro_onnx import Kokoro as KokoroONNX  # type: ignore
            import urllib.request

            model_dir = os.path.join(os.getcwd(), "temp", "kokoro")
            os.makedirs(model_dir, exist_ok=True)
            model_path  = os.path.join(model_dir, "kokoro-v1.0.onnx")
            voices_path = os.path.join(model_dir, "voices-v1.0.bin")

            _ONNX_MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
            _VOICES_URL     = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

            if not os.path.exists(model_path):
                logger.info("Downloading Kokoro ONNX model (~88 MB)... (one-time setup)")
                urllib.request.urlretrieve(_ONNX_MODEL_URL, model_path)
                logger.info("Kokoro model downloaded.")

            if not os.path.exists(voices_path):
                logger.info("Downloading Kokoro voices pack (~35 MB)... (one-time setup)")
                urllib.request.urlretrieve(_VOICES_URL, voices_path)
                logger.info("Voices downloaded.")

            self._kokoro = KokoroONNX(model_path, voices_path)
            self._kokoro_api = "onnx"
            logger.info("[OK] Kokoro-ONNX loaded (Python 3.13 compatible).")
            return
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"kokoro-onnx init failed: {e}")

        # Option 2: KPipeline (PyTorch, kokoro >= 0.9) ───────────────────
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            from kokoro import KPipeline  # type: ignore
            logger.info(f"Loading Kokoro KPipeline on {device.upper()}...")
            self._kokoro = KPipeline(lang_code="a", device=device)
            self._kokoro_api = "pipeline"
            logger.info("[OK] Kokoro-82M (KPipeline) loaded.")
            return
        except (ImportError, Exception):
            pass

        # Option 3: generate() API (kokoro 0.7.x) ─────────────────────────
        try:
            import kokoro as _kok  # type: ignore
            if hasattr(_kok, "generate"):
                self._kokoro = _kok
                self._kokoro_api = "generate"
                logger.info("[OK] Kokoro (generate API / 0.7.x) loaded.")
                return
        except ImportError:
            pass

        logger.warning(
            "Kokoro not installed. Install with:\n"
            "  pip install kokoro-onnx\n"
            "Falling back to Edge-TTS."
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_available(self) -> bool:
        return self._kokoro is not None

    @property
    def active_speaking(self) -> bool:
        return self._active

    def speak(
        self,
        text: str,
        emotion_label: str = "neutral",
        rate: float = 1.0,
        on_first_chunk: Optional[callable] = None,
        agent_id: Optional[str] = None,
    ):
        """
        Non-blocking speak. Synthesises and plays in a background thread.

        Args:
            text:           Pre-processed text (may contain [breath] etc. tokens).
            emotion_label:  One of the emotion labels from emotion_classifier.
            rate:           Speech rate multiplier (0.5 – 2.0).
            on_first_chunk: Callback invoked just before audio playback starts.
            agent_id:       Optional agent identifier to use a distinct voice.
        """
        with self._lock:
            self._stop()
            self._stop_event.clear()
            self._active = True

        if agent_id and agent_id in _AGENT_VOICE_MAP:
            voice_id = _AGENT_VOICE_MAP[agent_id]
        else:
            voice_id = _VOICE_MAP.get(emotion_label, _DEFAULT_VOICE)

        t = threading.Thread(
            target=self._synthesis_worker,
            args=(text, voice_id, rate, on_first_chunk),
            daemon=True,
        )
        t.start()

    def synthesize_to_file(self, text: str, output_path: str, emotion_label: str = "neutral", rate: float = 1.0) -> bool:
        """
        Synchronously synthesizes text to a WAV file (e.g. for WhatsApp voice notes).
        Returns True on success, False on failure.
        """
        import soundfile as sf

        voice_id = _VOICE_MAP.get(emotion_label, _DEFAULT_VOICE)

        try:
            segments = resolve_tokens(text)
            parts = []

            for seg in segments:
                if seg["type"] == "audio":
                    audio = humanize(seg["content"], apply_jitter=False)
                    parts.append(audio)
                elif seg["type"] == "text":
                    seg_text = seg["content"].strip()
                    if not seg_text:
                        continue
                    audio = self._synthesise_text(seg_text, voice_id, rate)
                    if audio is not None and len(audio) > 0:
                        parts.append(humanize(audio))

            if not parts:
                return False

            full_audio = np.concatenate(parts).astype(np.float32) / 32768.0
            sf.write(output_path, full_audio, SAMPLE_RATE)
            logger.info(f"[TTS] Voice note saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"synthesize_to_file error: {e}")
            return False


    def stop(self):
        """Interrupt ongoing speech immediately (barge-in)."""
        with self._lock:
            self._stop()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _stop(self):
        self._stop_event.set()
        self._active = False
        try:
            import sounddevice as sd
            sd.stop()
        except Exception:
            pass

    def _synthesis_worker(
        self,
        text: str,
        voice_id: str,
        rate: float,
        on_first_chunk: Optional[callable],
    ):
        """
        Collect-then-play pipeline:
          1. Resolve [breath]/[sigh] tokens into procedural audio.
          2. Synthesise all plain-text segments into numpy arrays.
          3. Concatenate everything into ONE array.
          4. Call sd.play() ONCE — one hardware open/close, zero internal gaps.

        This is the only architecture that guarantees no word-breaks or chunking.
        """
        import sounddevice as sd

        try:
            segments = resolve_tokens(text)
            parts: list[np.ndarray] = []

            for seg in segments:
                if self._stop_event.is_set():
                    return

                if seg["type"] == "audio":
                    # Procedural breath / sigh / laugh sound
                    audio = humanize(seg["content"], apply_jitter=False)
                    parts.append(audio)

                elif seg["type"] == "text":
                    seg_text = seg["content"].strip()
                    if not seg_text:
                        continue
                    audio = self._synthesise_text(seg_text, voice_id, rate)
                    if audio is not None and len(audio) > 0:
                        parts.append(humanize(audio))

            if not parts or self._stop_event.is_set():
                return

            # Concatenate ALL parts into one seamless float32 array
            full_audio = np.concatenate(parts).astype(np.float32) / 32768.0

            # Notify caller that audio is about to start
            if on_first_chunk:
                try:
                    on_first_chunk()
                except Exception:
                    pass

            # Single sd.play() — guaranteed no internal gaps
            sd.play(full_audio, samplerate=SAMPLE_RATE, blocking=False)

            # Wait for completion, honouring barge-in
            while sd.get_stream().active:
                if self._stop_event.is_set():
                    sd.stop()
                    break
                time.sleep(0.03)

        except Exception as e:
            logger.error(f"Synthesis worker error: {e}")
        finally:
            self._active = False

    def _synthesise_text(
        self, text: str, voice_id: str, rate: float
    ) -> Optional[np.ndarray]:
        """
        Synthesise a plain-text segment into a single int16 numpy array.
        Passes the FULL text to Kokoro — no sentence splitting —
        Kokoro handles its own phoneme batching internally.
        Returns None on failure.
        """
        # Strip custom tokens before reaching Kokoro's phonemiser
        text = _TOKEN_STRIP.sub('', text).strip()
        if not text:
            return None

        # Intercept cloned voice requests (e.g. clone:Voicesamp/female_ref.wav)
        if voice_id.startswith("clone:"):
            ref_path = voice_id.replace("clone:", "")
            url = "http://localhost:8768/synthesize"
            payload = {
                "text": text,
                "language": "en",
                "speaker_wav": os.path.abspath(ref_path)
            }
            logger.info(f"[XTTSv2] Requesting cloned synthesis for reference: {ref_path}")
            import requests
            import io
            import soundfile as sf
            try:
                res = requests.post(url, json=payload, timeout=25)
                if res.status_code == 200:
                    data, sr = sf.read(io.BytesIO(res.content), dtype='int16')
                    logger.info(f"[XTTSv2] Successfully synthesized {len(data)} samples at {sr}Hz.")
                    return data
                else:
                    logger.warning(f"[XTTSv2] Cloner server returned error {res.status_code}: {res.text}. Falling back to default Kokoro voice.")
            except Exception as e:
                logger.warning("[XTTSv2] Cloner server offline or unreachable. Falling back to default Kokoro voice.")
            # Fallback to default Kokoro voice ID if server fails
            voice_id = "af_heart"

        if not self._kokoro:
            return None

        try:
            if self._kokoro_api == "onnx":
                samples, _sr = self._kokoro.create(
                    text, voice=voice_id, speed=rate, lang="en-us"
                )
                if samples is not None and len(samples) > 0:
                    return (samples * 32767).clip(-32768, 32767).astype(np.int16)

            elif self._kokoro_api == "pipeline":
                chunks = []
                for _gs, _ps, audio in self._kokoro(text, voice=voice_id, speed=rate):
                    if self._stop_event.is_set():
                        break
                    if audio is not None and len(audio) > 0:
                        chunks.append((audio * 32767).clip(-32768, 32767).astype(np.int16))
                if chunks:
                    return np.concatenate(chunks)

            elif self._kokoro_api == "generate":
                audio, _ = self._kokoro.generate(text, voice=voice_id, speed=rate)
                if audio is not None and len(audio) > 0:
                    return (audio.numpy() * 32767).clip(-32768, 32767).astype(np.int16)

        except Exception as e:
            logger.error(f"Synthesis error: {e}")

        return None


# ---------------------------------------------------------------------------
# Edge-TTS fallback engine
# ---------------------------------------------------------------------------

class EdgeTTSFallback:
    """
    Lightweight fallback using edge-tts when Kokoro is unavailable.
    """

    VOICE_MAP: dict[str, str] = {
        "neutral":    "en-US-AriaNeural",
        "happy":      "en-US-JennyNeural",
        "excited":    "en-US-SaraNeural",
        "sad":        "en-US-GuyNeural",
        "depressed":  "en-US-DavisNeural",
        "angry":      "en-US-TonyNeural",
        "thoughtful": "en-US-AriaNeural",
        "laugh":      "en-US-JennyNeural",
    }

    RATE_MAP: dict[str, str] = {
        "neutral":    "+0%",
        "happy":      "+10%",
        "excited":    "+15%",
        "sad":        "-15%",
        "depressed":  "-20%",
        "angry":      "+10%",
        "thoughtful": "-5%",
        "laugh":      "+5%",
    }

    def __init__(self):
        self._active = False
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._temp_dir = os.path.join(os.getcwd(), "temp", "tts")
        os.makedirs(self._temp_dir, exist_ok=True)

    @property
    def active_speaking(self) -> bool:
        return self._active

    def speak(self, text: str, emotion_label: str = "neutral", rate: float = 1.0, **kwargs):
        """Non-blocking speak with edge-tts."""
        with self._lock:
            self._stop_event.clear()
            self._active = True

        t = threading.Thread(
            target=self._worker,
            args=(text, emotion_label),
            daemon=True,
        )
        t.start()

    def stop(self):
        self._stop_event.set()
        self._active = False

    def _worker(self, text: str, emotion: str):
        try:
            import asyncio
            import edge_tts
            import soundfile as sf
            import sounddevice as sd

            clean = _TOKEN_STRIP.sub('', text).strip()
            voice = self.VOICE_MAP.get(emotion, "en-US-AriaNeural")
            rate_str = self.RATE_MAP.get(emotion, "+0%")
            output_file = os.path.join(self._temp_dir, "edge_fallback.mp3")

            async def _generate():
                communicate = edge_tts.Communicate(clean, voice, rate=rate_str)
                await communicate.save(output_file)

            asyncio.run(_generate())

            if self._stop_event.is_set():
                return

            data, sr = sf.read(output_file, dtype='float32')
            sd.play(data, samplerate=sr, blocking=True)
        except Exception as e:
            logger.error(f"EdgeTTS fallback error: {e}")
        finally:
            self._active = False


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = KokoroTTSEngine()

    if engine.is_available:
        print("\n[OK] Kokoro available - testing emotional voices\n")
        tests = [
            ("I'm so happy right now! Everything is going perfectly!", "happy"),
            ("I just don't know. It's all so heavy and I feel lost.", "depressed"),
            ("Haha, okay that was actually hilarious, I wasn't expecting that!", "laugh"),
            ("This is completely unacceptable. I am furious right now.", "angry"),
            ("Hmm. Let me think about that for a moment... yes, I think you're right.", "thoughtful"),
        ]
        for text, emotion in tests:
            print(f"[{emotion.upper()}] {text}")
            engine.speak(text, emotion_label=emotion)
            time.sleep(0.2)
            while engine.active_speaking:
                time.sleep(0.05)
            time.sleep(0.3)
    else:
        print("\n[WARN] Kokoro not installed. Testing Edge-TTS fallback...")
        fallback = EdgeTTSFallback()
        fallback.speak("Hello, I am using the Edge-TTS fallback voice.", "neutral")
        time.sleep(4)
