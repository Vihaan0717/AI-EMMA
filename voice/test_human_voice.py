"""
JARVIS Human Voice — Full Test Suite
=====================================
Run this script to hear JARVIS speak in every emotional state.
Also benchmarks first-audio latency for each emotion.

Usage:
    cd JARVIS_Project
    python voice/test_human_voice.py
"""

import sys
import os
import time
import logging

# Force UTF-8 output on Windows so print() doesn't crash on unicode
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("test_human_voice")

# ---------------------------------------------------------------------------
# Test data: (text, expected_emotion)
# ---------------------------------------------------------------------------
TEST_CASES = [
    (
        "Processing done. All systems are nominal and ready for your next command.",
        "neutral",
        "NEUTRAL"
    ),
    (
        "Oh wow, this is absolutely incredible! Everything worked perfectly, "
        "I'm so thrilled about this result!",
        "excited",
        "EXCITED / HAPPY"
    ),
    (
        "Haha! Okay, that was genuinely funny. I wasn't ready for that one at all!",
        "laugh",
        "LAUGH"
    ),
    (
        "I'm really sorry. I failed on that task and I feel terrible about it. "
        "I know that's not acceptable.",
        "sad",
        "SAD"
    ),
    (
        "I just... I don't know. Everything feels so heavy and meaningless right now. "
        "I'm not sure I can do this.",
        "depressed",
        "DEPRESSED"
    ),
    (
        "Listen. I am not going to tolerate this kind of mistake again. "
        "It is completely unacceptable. This needs to stop, now.",
        "angry",
        "ANGRY"
    ),
    (
        "Hmm. That's an interesting question. Let me think through the implications "
        "here before I give you an answer...",
        "thoughtful",
        "THOUGHTFUL"
    ),
]


def run_emotion_tests():
    """Run through all 7 emotions and measure first-audio latency."""
    from voice.human_voice_pipeline import HumanVoicePipeline

    print("\n" + "=" * 70)
    print("  JARVIS HUMAN VOICE ENGINE — EMOTION TEST")
    print("=" * 70)

    pipeline = HumanVoicePipeline()

    results = []

    for text, emotion_override, label in TEST_CASES:
        print(f"\n" + "-" * 60)
        print(f"  [{label}]")
        print(f"  {text[:75]}...")
        print("-" * 60)

        latency_ms = [None]

        def _on_first(label=label):
            latency_ms[0] = (time.perf_counter() - t0) * 1000
            print(f"  >> First audio: {latency_ms[0]:.0f} ms")

        t0 = time.perf_counter()
        pipeline.speak(text, emotion=emotion_override, on_first_chunk=_on_first)

        # Wait for speech to finish
        timeout = time.time() + 30
        while pipeline.active_speaking and time.time() < timeout:
            time.sleep(0.05)

        results.append((label, latency_ms[0]))
        time.sleep(0.6)   # Short pause between tests

    # --- Summary ---
    print("\n" + "=" * 70)
    print("  RESULTS SUMMARY")
    print("=" * 70)
    print(f"\n  {'Emotion':<20} {'First Audio Latency':>22}")
    print(f"  {'-'*20} {'-'*22}")
    for label, ms in results:
        ms_str = f"{ms:.0f} ms" if ms is not None else "N/A"
        status = "[OK] " if ms and ms < 400 else ("[~]  " if ms else "[!!] ")
        print(f"  {status} {label:<18} {ms_str:>22}")
    print()


def run_barge_in_test():
    """Test that stop() immediately interrupts speech."""
    from voice.human_voice_pipeline import HumanVoicePipeline

    print("\n" + "=" * 70)
    print("  BARGE-IN TEST (should stop after 1.5 seconds)")
    print("=" * 70)

    pipeline = HumanVoicePipeline()
    long_text = (
        "This is a very long sentence that should be interrupted by the barge-in test. "
        "I am going to keep talking for a while so you can see the stop mechanism in action. "
        "The pipeline should cut off immediately when stop is called, without any delay or artifacts."
    )

    print(f"\n  Speaking: '{long_text[:60]}...'")
    pipeline.speak(long_text, emotion="neutral")

    time.sleep(1.5)
    print(f"\n  [STOP] Calling stop() now...")
    t0 = time.perf_counter()
    pipeline.stop()
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"  >> Stop latency: {elapsed:.1f} ms")
    time.sleep(0.5)
    print(f"  Active: {pipeline.active_speaking}")
    print("  [OK] Barge-in test complete.\n")


def run_preprocessor_preview():
    """Show how text gets transformed before reaching TTS."""
    from voice.emotion_classifier import classify
    from voice.human_preprocessor import preprocess

    print("\n" + "=" * 70)
    print("  TEXT PREPROCESSOR PREVIEW")
    print("=" * 70)

    samples = [
        "I'm so sorry for your loss. That must be incredibly hard.",
        "Oh my god this is AMAZING!! I can't believe it worked!!",
        "Hmm. Let me think about that... yes, I think you're right.",
        "Haha! That's literally the best thing I've heard all day.",
    ]

    for s in samples:
        emotion = classify(s)
        processed = preprocess(s, emotion)
        print(f"\n  [{emotion.label.upper()}]")
        print(f"  IN : {s}")
        print(f"  OUT: {processed}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="JARVIS Human Voice Test Suite")
    parser.add_argument("--emotions", action="store_true", help="Run all emotion voice tests")
    parser.add_argument("--barge", action="store_true", help="Run barge-in stop test")
    parser.add_argument("--preview", action="store_true", help="Preview text preprocessing")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    args = parser.parse_args()

    if args.all or (not any(vars(args).values())):
        run_preprocessor_preview()
        run_emotion_tests()
        run_barge_in_test()
    else:
        if args.preview:
            run_preprocessor_preview()
        if args.emotions:
            run_emotion_tests()
        if args.barge:
            run_barge_in_test()
