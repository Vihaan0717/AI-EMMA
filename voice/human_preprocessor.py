"""
JARVIS Human Text Preprocessor
================================
Transforms plain response text into speech-ready text with:
  - Breathing markers at natural clause boundaries
  - Sighs and exhausted sounds (sad / depressed)
  - Laughter phonemes (happy / laugh)
  - Filler sounds: "hmm", "uhh", "ugh"
  - Pause markup as SSML-compatible silence inserts (comma/dash/ellipsis)
  - Emotional sentence starters

The output feeds directly into the Kokoro TTS engine.
All markers use a simple `[TAG]` syntax that the audio_humanizer resolves
into actual audio events.
"""

import re
import random
from voice.emotion_classifier import EmotionResult


# ---------------------------------------------------------------------------
# Sound stubs that are replaced by actual audio clips in the humanizer
# ---------------------------------------------------------------------------
BREATH_TOKEN  = "[breath]"   # ~200ms soft inhale sound
SIGH_TOKEN    = "[sigh]"     # ~600ms long sigh
LAUGH_TOKEN   = "[laugh]"    # ~400ms chuckle sound
HMM_TOKEN     = "[hmm]"      # ~200ms thoughtful "hmm"
EXHALE_TOKEN  = "[exhale]"   # ~300ms tired exhale
PAUSE_SHORT   = "[pause:0.2]"  # 200ms silence
PAUSE_MED     = "[pause:0.4]"  # 400ms silence
PAUSE_LONG    = "[pause:0.7]"  # 700ms silence


# ---------------------------------------------------------------------------
# Filler / starter phrases per emotion
# ---------------------------------------------------------------------------
_STARTERS = {
    "sad":       ["Honestly... ",  "Look, ", "The thing is... ", "I mean... "],
    "depressed": ["*sigh* ", "I... ", "I don't know... ", "It's just... "],
    "angry":     ["Alright. ", "Listen. ", "I'll be straight with you. ", "Okay. So. "],
    "thoughtful":["Hmm. ", "Well... ", "That's a good point. ", "Let me think... "],
    "happy":     ["Oh, ", "Great news! ", "Alright! ", "So! "],
    "excited":   ["Oh wow! ", "Okay so — ", "This is HUGE — ", "Right! "],
    "laugh":     ["Ha — okay, ", "Heh. ", "Alright, haha, "],
    "neutral":   [],
}

_SIGH_ENDERS = [". *sigh*", "...", ". Yeah.", "... anyway."]

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------
_LONG_SENTENCE_RE  = re.compile(r'(.{60,}?(?:,|;|—|–|\band\b|\bor\b|\bbut\b|\bso\b))', re.DOTALL)
_ELLIPSIS_RE       = re.compile(r'\.\.\.')
_DASH_RE           = re.compile(r'\s*[—–]\s*')
_LAUGH_WORDS_RE    = re.compile(r'\b(haha|hehe|lol|lmao|hahaha)\b', re.IGNORECASE)
_HMMS_RE           = re.compile(r'\bhmm+\b', re.IGNORECASE)
_UGH_RE            = re.compile(r'\bugh+\b', re.IGNORECASE)
_EXCLAMATION_RE    = re.compile(r'!+')
_SENTENCE_END_RE   = re.compile(r'([.!?])\s+')


def preprocess(text: str, emotion: EmotionResult) -> str:
    """
    Main entry point. Returns speech-ready text with human sound markers.
    
    Args:
        text:    Raw LLM response text.
        emotion: Result from emotion_classifier.classify()
    
    Returns:
        String with [breath], [sigh], [laugh] tokens and extra punctuation
        pauses injected. This string is passed to Kokoro TTS.
    """
    label     = emotion.label
    intensity = emotion.intensity

    # 1. Clean up markdown / symbols
    text = _clean_markdown(text)

    # 2. Inject emotional starter
    starters = _STARTERS.get(label, [])
    if starters and random.random() < 0.6:
        text = random.choice(starters) + text

    # 3. Replace laugh words with phoneme tokens
    text = _LAUGH_WORDS_RE.sub(f"{LAUGH_TOKEN}", text)

    # 4. Replace filler words
    text = _HMMS_RE.sub(f"{HMM_TOKEN}", text)
    text = _UGH_RE.sub(f"{EXHALE_TOKEN}", text)

    # 5. Ellipsis → long pause + breath
    text = _ELLIPSIS_RE.sub(f"{PAUSE_LONG}", text)

    # 6. Dashes → medium pause
    text = _DASH_RE.sub(f" {PAUSE_MED} ", text)

    # 7. Inject breath at long clause boundaries
    if emotion.breath_density > 0.3:
        text = _inject_breaths(text, emotion.breath_density)

    # 8. Emotion-specific lead-ins
    if label in ("sad", "depressed") and intensity > 0.6:
        text = SIGH_TOKEN + " " + text

    if label == "depressed" and intensity > 0.7:
        # Add trailing sigh if text ends normally
        if text.rstrip().endswith(('.', '!')):
            text = text.rstrip() + " " + random.choice(_SIGH_ENDERS)

    # 9. Short excited interjections
    if label == "excited" and intensity > 0.7:
        text = _boost_exclamations(text)

    # 10. Final cleanup – remove doubled spaces, multiple tokens in a row
    text = re.sub(r'(\[(?:breath|sigh|hmm|exhale|laugh)\])\s*\1', r'\1', text)
    text = re.sub(r'  +', ' ', text)
    text = text.strip()

    return text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_markdown(text: str) -> str:
    """Remove markdown bold, italic, code, headers."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)   # **bold**
    text = re.sub(r'\*(.+?)\*',     r'\1', text)   # *italic*
    text = re.sub(r'`(.+?)`',       r'\1', text)   # `code`
    text = re.sub(r'#{1,6}\s+',     '',    text)   # # headers
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # [links](url)
    text = re.sub(r'[-*•]\s+', '', text)            # bullet points
    return text


def _inject_breaths(text: str, density: float) -> str:
    """Insert BREATH_TOKEN after long clause segments based on density."""
    sentences = _SENTENCE_END_RE.split(text)
    result_parts = []
    char_since_breath = 0

    threshold = int(120 / max(density, 0.1))   # higher density → shorter threshold

    for part in sentences:
        result_parts.append(part)
        char_since_breath += len(part)
        if char_since_breath >= threshold and random.random() < density:
            result_parts.append(f" {BREATH_TOKEN} ")
            char_since_breath = 0

    return ''.join(result_parts)


def _boost_exclamations(text: str) -> str:
    """Replace ! with more energetic phrasing."""
    def _repl(m):
        return random.choice(["!", "!!", "! "])
    return _EXCLAMATION_RE.sub(_repl, text)


# ---------------------------------------------------------------------------
# Preview / test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from voice.emotion_classifier import classify, EmotionResult

    samples = [
        "I'm so sorry for the loss, it must be really difficult. Losing someone close is never easy...",
        "I can't believe how AMAZING this is!! This is the best day ever — everything is falling into place!",
        "Hmm. That's an interesting approach. Let me think about the trade-offs here.",
        "Ugh. Fine. I'll do it. But I want you to know I disagree with this completely.",
        "Haha okay that's actually hilarious, I wasn't expecting that at all.",
        "Processing done. The file has been saved to the output directory.",
    ]

    for s in samples:
        emotion = classify(s)
        processed = preprocess(s, emotion)
        print(f"\n[{emotion.label.upper()}] ({emotion.intensity:.2f})")
        print(f"  IN:  {s[:80]}")
        print(f"  OUT: {processed[:100]}")
