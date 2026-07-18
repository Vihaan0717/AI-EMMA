"""
JARVIS Emotion Classifier
=========================
Ultra-fast (<1ms) keyword + pattern classifier that maps any response text
to one of 7 emotional states. Drives voice prosody, breath patterns, and
pace in the HumanVoicePipeline.

NO LLM, NO API — pure Python logic.
"""

import re
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Emotion data structure
# ---------------------------------------------------------------------------
@dataclass
class EmotionResult:
    label: str          # canonical label
    intensity: float    # 0.0 – 1.0
    voice_id: str       # Kokoro voice identifier
    rate: float         # speech rate multiplier (1.0 = normal)
    pitch_shift: float  # semitones shift  (+1.5 = higher, -1.5 = lower)
    breath_density: float  # 0.0 – 1.0 how often to inject breath sounds


# ---------------------------------------------------------------------------
# Emotion definitions
# ---------------------------------------------------------------------------
_EMOTIONS: dict[str, dict] = {
    "laugh": {
        "voice_id": "af_bella",
        "rate": 1.0,
        "pitch_shift": 1.0,
        "breath_density": 0.5,
    },
    "excited": {
        "voice_id": "af_bella",
        "rate": 1.2,
        "pitch_shift": 1.5,
        "breath_density": 0.3,
    },
    "happy": {
        "voice_id": "af_bella",
        "rate": 1.1,
        "pitch_shift": 0.8,
        "breath_density": 0.2,
    },
    "angry": {
        "voice_id": "am_michael",
        "rate": 1.15,
        "pitch_shift": -0.5,
        "breath_density": 0.6,
    },
    "sad": {
        "voice_id": "am_adam",
        "rate": 0.85,
        "pitch_shift": -1.5,
        "breath_density": 0.8,
    },
    "depressed": {
        "voice_id": "am_adam",
        "rate": 0.78,
        "pitch_shift": -2.0,
        "breath_density": 1.0,
    },
    "thoughtful": {
        "voice_id": "af_heart",
        "rate": 0.92,
        "pitch_shift": 0.0,
        "breath_density": 0.4,
    },
    "neutral": {
        "voice_id": "af_heart",
        "rate": 1.0,
        "pitch_shift": 0.0,
        "breath_density": 0.25,
    },
}

# ---------------------------------------------------------------------------
# Keyword / pattern triggers
# ---------------------------------------------------------------------------
_RULES: list[tuple[str, float, re.Pattern]] = [
    # (emotion_label, base_intensity, compiled_regex)
    ("laugh",   0.9, re.compile(
        r"\b(haha|hehe|lol|lmao|hilarious|funny|laugh|giggle|joke|amusing|hahaha|😂|😄|🤣)\b",
        re.IGNORECASE
    )),
    ("excited", 0.85, re.compile(
        r"\b(amazing|incredible|awesome|wow|fantastic|unbelievable|blast|thrilling|"
        r"super excited|can't wait|omg|oh my god|🔥|🎉|🚀)\b",
        re.IGNORECASE
    )),
    ("happy",   0.75, re.compile(
        r"\b(great|happy|glad|pleased|wonderful|delighted|love|enjoy|perfect|excellent|"
        r"brilliant|joy|yay|sweet|nice|good news|😊|😁|🙂)\b",
        re.IGNORECASE
    )),
    ("angry",   0.85, re.compile(
        r"\b(angry|furious|outraged|unacceptable|ridiculous|pathetic|stupid|idiot|"
        r"infuriating|damn|frustrated|irritated|annoy|hate|😤|😠|🤬)\b",
        re.IGNORECASE
    )),
    ("depressed", 0.9, re.compile(
        r"\b(depressed|hopeless|worthless|meaningless|can'?t go on|no point|"
        r"giving up|broken|devastated|numb|empty|lost everything|😔|💔|😞|😢)\b",
        re.IGNORECASE
    )),
    ("sad",     0.75, re.compile(
        r"\b(sad|sorry|unfortunately|regret|miss|lost|failed|disappointing|"
        r"heartbroken|grief|mourn|painful|hurt|difficult|😢|😥|😭)\b",
        re.IGNORECASE
    )),
    ("thoughtful", 0.6, re.compile(
        r"\b(hmm|well|interesting|wonder|perhaps|consider|think|reflect|ponder|"
        r"maybe|possibly|actually|curious|intriguing|🤔)\b",
        re.IGNORECASE
    )),
]

# Intensity boosters from punctuation / structure
_EXCLAMATION_RE = re.compile(r"!+")
_QUESTION_RE    = re.compile(r"\?")
_ELLIPSIS_RE    = re.compile(r"\.\.\.")
_CAPS_RE        = re.compile(r"\b[A-Z]{3,}\b")


def classify(text: str, override: Optional[str] = None) -> EmotionResult:
    """
    Classify the emotional content of a response text.
    
    Args:
        text: The response string to classify.
        override: Force a specific emotion label (for testing / manual control).
    
    Returns:
        EmotionResult with voice settings tuned to the detected emotion.
    """
    if override and override in _EMOTIONS:
        cfg = _EMOTIONS[override]
        return EmotionResult(label=override, intensity=0.8, **cfg)

    scores: dict[str, float] = {e: 0.0 for e in _EMOTIONS}

    # --- Pattern matching ---
    for label, base_intensity, pattern in _RULES:
        matches = pattern.findall(text)
        if matches:
            scores[label] += base_intensity * min(len(matches), 3)

    # --- Structural modifiers ---
    exclamations = len(_EXCLAMATION_RE.findall(text))
    caps_count   = len(_CAPS_RE.findall(text))
    ellipsis_cnt = len(_ELLIPSIS_RE.findall(text))

    if exclamations >= 2 or caps_count >= 2:
        # Amplify positive emotions
        scores["excited"] += 0.3
        scores["angry"]   += 0.2

    if ellipsis_cnt >= 2:
        scores["thoughtful"] += 0.25
        scores["sad"]        += 0.1

    # --- Text length heuristic ---
    word_count = len(text.split())
    if word_count < 8:
        scores["neutral"] += 0.2   # Very short replies tend to be neutral

    # --- Pick the winner ---
    best_label = max(scores, key=lambda l: scores[l])
    best_score = scores[best_label]

    if best_score < 0.3:
        best_label = "neutral"
        best_score = 0.5

    cfg = _EMOTIONS[best_label]
    return EmotionResult(
        label=best_label,
        intensity=min(best_score, 1.0),
        voice_id=cfg["voice_id"],
        rate=cfg["rate"],
        pitch_shift=cfg["pitch_shift"],
        breath_density=cfg["breath_density"],
    )


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    samples = [
        ("I'm so happy today, everything is going great!", None),
        ("This is absolutely infuriating, I can't believe this!", None),
        ("I feel so lost and empty, nothing makes sense anymore.", None),
        ("Haha that was hilarious! I can't stop laughing.", None),
        ("Hmm, that's an interesting question, let me think about it...", None),
        ("Okay, done. The file has been saved.", None),
        ("WOW this is INCREDIBLE!! I'm blown away!!", None),
    ]
    print(f"\n{'Text':<55} {'Emotion':<12} {'Rate':<6} {'Pitch'}")
    print("-" * 85)
    for txt, ovr in samples:
        r = classify(txt, ovr)
        print(f"{txt[:54]:<55} {r.label:<12} {r.rate:<6.2f} {r.pitch_shift:+.1f}")
