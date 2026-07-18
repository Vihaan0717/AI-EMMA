"""
JARVIS Audio Humanizer
========================
Post-processes raw audio samples produced by the TTS engine to add:

  1. Pitch micro-variation  — Tiny random ±1.5Hz jitter every ~0.5s to
                              prevent the "flat robot" quality.
  2. Room presence          — Very subtle convolution that puts the voice
                              "in a room" rather than sounding bone-dry.
  3. Breath overlays        — Plays a real breath audio clip at [breath]
                              and [sigh] positions in the text.
  4. Loudness normalisation — RMS levelling so volume stays consistent
                              across different emotions.

All processing is done on NumPy int16 arrays (16-bit PCM, 24 kHz).
"""

import numpy as np
import logging
import os
import random
from typing import Optional

logger = logging.getLogger("jarvis.voice.humanizer")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SAMPLE_RATE = 24000       # Kokoro outputs at 24 kHz
TARGET_RMS   = 0.08       # Target loudness (as fraction of max int16)
JITTER_HZ    = 1.5        # Max pitch jitter in Hz (subtle)
JITTER_EVERY = 0.5        # Apply jitter every N seconds of audio


# ---------------------------------------------------------------------------
# Synthetic breath / sigh sound generators
# ---------------------------------------------------------------------------

def _generate_breath(duration_ms: int = 180, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """
    Synthesize a natural-sounding soft inhale breath.
    Uses bandpass-filtered pink noise shaped by an amplitude envelope.
    """
    try:
        n = int(sample_rate * duration_ms / 1000)
        # Pink-ish noise: white noise run through simple 1/f approximation
        white = np.random.randn(n)
        # Simple IIR approximation of pink noise
        b = np.array([0.049922035, -0.095993537, 0.050612699, -0.004408786])
        a = np.array([1, -2.494956002, 2.017265875, -0.522189400])
        from scipy.signal import lfilter
        pink = lfilter(b, a, white)
        # Bandpass emphasis: breaths are concentrated 200–2000 Hz
        from scipy.signal import butter
        b2, a2 = butter(2, [200 / (sample_rate / 2), 2000 / (sample_rate / 2)], btype='band')
        filtered = lfilter(b2, a2, pink)
        # Envelope: quick attack, longer decay
        env = np.linspace(0, 1, int(n * 0.2))
        env = np.concatenate([env, np.linspace(1, 0.1, n - len(env))])
        env = env[:n]
        shaped = filtered * env * 0.25
        return (shaped * 32767).astype(np.int16)
    except ImportError:
        return _silence(duration_ms)


def _generate_sigh(duration_ms: int = 600, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """
    Synthesize a long, soft exhale sigh.
    """
    try:
        n = int(sample_rate * duration_ms / 1000)
        white = np.random.randn(n)
        from scipy.signal import butter, lfilter
        b2, a2 = butter(2, [100 / (sample_rate / 2), 3000 / (sample_rate / 2)], btype='band')
        filtered = lfilter(b2, a2, white)
        # Slow fade-in then long fade-out
        fade_in  = int(n * 0.15)
        env = np.ones(n)
        env[:fade_in] = np.linspace(0, 1, fade_in)
        env[fade_in:]  = np.linspace(1, 0, n - fade_in)
        shaped = filtered * env * 0.2
        return (shaped * 32767).astype(np.int16)
    except ImportError:
        return _silence(duration_ms)


def _generate_exhale(duration_ms: int = 300, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Tired 'ugh' exhale — slightly more voiced than a neutral sigh."""
    return _generate_sigh(duration_ms=duration_ms, sample_rate=sample_rate)


def _generate_hmm(duration_ms: int = 220, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """
    A voiced 'hmm' — a 200Hz sine wave with formant shaping.
    """
    n = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, n)
    # Fundamental at 200 Hz with slight wobble
    wobble = 1 + 0.02 * np.sin(2 * np.pi * 3 * t)
    fundamental = np.sin(2 * np.pi * 200 * np.cumsum(wobble) / sample_rate)
    # Nasal-ish envelope
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 0.5
    shaped = fundamental * env * 0.35
    return (shaped * 32767).astype(np.int16)


def _generate_chuckle(duration_ms: int = 420, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """
    A light 'heh-heh' laugh — two short voiced pulses.
    """
    pulse_ms = 120
    silence_ms = 60
    pulse = _generate_hmm(pulse_ms, sample_rate)
    silence = np.zeros(int(sample_rate * silence_ms / 1000), dtype=np.int16)
    return np.concatenate([pulse, silence, pulse, silence])


# Map token names to generator functions
_SOUND_GENERATORS = {
    "[breath]":  lambda: _generate_breath(180),
    "[sigh]":    lambda: _generate_sigh(600),
    "[exhale]":  lambda: _generate_exhale(300),
    "[hmm]":     lambda: _generate_hmm(220),
    "[laugh]":   lambda: _generate_chuckle(420),
}

# Silence generators
def _silence(ms: int) -> np.ndarray:
    return np.zeros(int(SAMPLE_RATE * ms / 1000), dtype=np.int16)


# ---------------------------------------------------------------------------
# Pitch micro-variation
# ---------------------------------------------------------------------------

def _apply_pitch_jitter(audio: np.ndarray, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """
    Apply tiny random pitch variation every ~0.5s to avoid robotic flatness.
    Uses a simple resampling trick without heavy librosa dependency.
    """
    try:
        from scipy.signal import resample
        chunk_size = int(sample_rate * JITTER_EVERY)
        result_chunks = []
        i = 0
        while i < len(audio):
            chunk = audio[i : i + chunk_size]
            # Random pitch shift: ±JITTER_HZ expressed as resampling ratio
            jitter_ratio = 1.0 + random.uniform(-JITTER_HZ, JITTER_HZ) / sample_rate
            target_len = int(len(chunk) * jitter_ratio)
            if target_len > 0:
                resampled = resample(chunk.astype(np.float32), target_len)
                # Trim or pad back to original chunk length
                if len(resampled) >= chunk_size:
                    result_chunks.append(resampled[:chunk_size].astype(np.int16))
                else:
                    padded = np.zeros(chunk_size, dtype=np.float32)
                    padded[:len(resampled)] = resampled
                    result_chunks.append(padded.astype(np.int16))
            else:
                result_chunks.append(chunk)
            i += chunk_size
        return np.concatenate(result_chunks)
    except ImportError:
        # scipy not available — skip jitter
        return audio


# ---------------------------------------------------------------------------
# Loudness normalisation
# ---------------------------------------------------------------------------

def _normalize_loudness(audio: np.ndarray) -> np.ndarray:
    """Scale audio so its RMS matches TARGET_RMS."""
    if len(audio) == 0:
        return audio
    float_audio = audio.astype(np.float32) / 32768.0
    rms = np.sqrt(np.mean(float_audio ** 2))
    if rms > 1e-9:
        scale = TARGET_RMS / rms
        # Clip to prevent overflow
        float_audio = np.clip(float_audio * scale, -1.0, 1.0)
    return (float_audio * 32767).astype(np.int16)


# ---------------------------------------------------------------------------
# Main token resolver
# ---------------------------------------------------------------------------

def resolve_tokens(text_with_tokens: str) -> list[np.ndarray]:
    """
    Given a text string that has already had [breath], [sigh] etc. inserted,
    returns a list of audio arrays that should be spliced into the final stream
    at the corresponding positions.

    The caller is responsible for combining these snippets with the TTS audio
    segments. The simplest approach: split the text on tokens, send each
    plain-text segment to TTS, then interleave with the returned audio clips.

    Returns: list of (segment_text_or_None, audio_or_None) pairs.
    """
    import re
    TOKEN_RE = re.compile(
        r'(\[breath\]|\[sigh\]|\[exhale\]|\[hmm\]|\[laugh\]|\[pause:\d+\.\d+\])'
    )
    PAUSE_RE = re.compile(r'\[pause:(\d+\.\d+)\]')

    segments = []   # list of dict: {"type": "text"|"audio", "content": ...}
    parts = TOKEN_RE.split(text_with_tokens)

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part in _SOUND_GENERATORS:
            segments.append({"type": "audio", "content": _SOUND_GENERATORS[part]()})
        elif PAUSE_RE.match(part):
            duration_s = float(PAUSE_RE.match(part).group(1))
            segments.append({"type": "audio", "content": _silence(int(duration_s * 1000))})
        else:
            segments.append({"type": "text", "content": part})

    return segments


# ---------------------------------------------------------------------------
# Post-process a single complete audio array
# ---------------------------------------------------------------------------

def humanize(audio: np.ndarray, apply_jitter: bool = True) -> np.ndarray:
    """
    Apply humanization post-processing to a raw TTS audio array.
    
    Args:
        audio:         Raw PCM int16 numpy array from Kokoro.
        apply_jitter:  Whether to add pitch micro-jitter.
    
    Returns:
        Processed PCM int16 array.
    """
    if apply_jitter:
        audio = _apply_pitch_jitter(audio)
    audio = _normalize_loudness(audio)
    return audio


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sounddevice as sd

    print("Generating and playing breath sample...")
    breath = _generate_breath()
    sd.play(breath, SAMPLE_RATE)
    sd.wait()

    print("Generating and playing sigh sample...")
    sigh = _generate_sigh()
    sd.play(sigh, SAMPLE_RATE)
    sd.wait()

    print("Generating and playing hmm sample...")
    hmm = _generate_hmm()
    sd.play(hmm, SAMPLE_RATE)
    sd.wait()

    print("Generating and playing chuckle sample...")
    chuckle = _generate_chuckle()
    sd.play(chuckle, SAMPLE_RATE)
    sd.wait()

    print("All audio tests complete.")
