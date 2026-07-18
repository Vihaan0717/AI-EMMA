"""
═══════════════════════════════════════════════════════════════
PHONETIC MATCHER
Finds words in JARVIS's brain that SOUND similar
to an unknown word.

If JARVIS doesn't know "chestunnav" exactly,
but knows "chestunna" and "av" separately,
the phonetic matcher finds that connection.

Uses:
  → Edit distance (how many changes to get from word A to B)
  → Phoneme similarity (sounds that are easily confused)
  → Suffix stripping (remove endings, compare roots)
═══════════════════════════════════════════════════════════════
"""

from difflib import SequenceMatcher
from typing import Optional
from brain.neurons.neural_graph import NeuralGraph


# ═══════════════════════════════════════════════════════════════
# PHONETICALLY SIMILAR SOUND GROUPS
# Letters/sounds that are easily confused
# ═══════════════════════════════════════════════════════════════

PHONETIC_GROUPS = [
    # Vowel equivalents
    {"aa", "a", "aa"},
    {"ee", "i", "ii", "e"},
    {"oo", "u", "uu", "o"},
    {"ai", "ay", "ei"},
    {"au", "ow", "ou"},

    # Consonant pairs that sound similar
    {"b",  "bh"},
    {"d",  "dh", "da"},
    {"g",  "gh"},
    {"k",  "kh", "c"},
    {"p",  "ph", "f"},
    {"t",  "th", "ta"},
    {"sh", "s",  "sa"},
    {"v",  "w",  "va"},
    {"n",  "na", "m"},
    {"r",  "ra", "rr"},
    {"l",  "la", "ll"},
    {"ch", "c",  "cha"},
    {"j",  "ja", "jh"},

    # Common Telugu-specific equivalents
    {"nna", "na", "n"},
    {"stu", "st"},
    {"ttu", "tu", "tt"},
    {"ddu", "du", "dd"},
    {"kku", "ku", "kk"},
]


def phonetic_similarity(word1: str, word2: str) -> float:
    """
    Calculate how phonetically similar two words are.
    Returns 0.0 (completely different) to 1.0 (identical).
    """
    w1 = word1.lower().strip()
    w2 = word2.lower().strip()

    if w1 == w2:
        return 1.0

    # ── Basic sequence similarity ────────────────────────
    base_score = SequenceMatcher(None, w1, w2).ratio()

    # ── Boost if one contains the other ─────────────────
    if w1 in w2 or w2 in w1:
        base_score = max(base_score, 0.7)

    # ── Check phoneme group similarity ──────────────────
    phoneme_boost = _phoneme_group_similarity(w1, w2)

    return min(1.0, base_score + phoneme_boost)


def _phoneme_group_similarity(w1: str, w2: str) -> float:
    """Boost score if words share phonetically similar sounds"""
    boost = 0.0
    for group in PHONETIC_GROUPS:
        # Check if either word contains any sound in this group
        w1_has = any(sound in w1 for sound in group)
        w2_has = any(sound in w2 for sound in group)
        if w1_has and w2_has:
            boost += 0.05
    return min(boost, 0.2)


class PhoneticMatcher:
    """
    Searches JARVIS's neural brain for words that
    sound similar to an unknown input word.
    """

    def __init__(self, brain: NeuralGraph):
        self.brain = brain

    def find_similar(
        self,
        unknown_word:   str,
        top_n:          int   = 5,
        min_similarity: float = 0.4
    ) -> list[dict]:
        """
        Search the entire brain for neurons
        whose labels sound similar to unknown_word.

        Returns list of matches sorted by similarity.
        """
        unknown_word = unknown_word.lower().strip()
        matches = []

        for label, neuron_id in self.brain._label_index.items():
            if label == unknown_word:
                continue  # Skip exact match (handled elsewhere)

            score = phonetic_similarity(unknown_word, label)

            if score >= min_similarity:
                neuron = self.brain._neurons.get(neuron_id)
                if neuron:
                    matches.append({
                        "label":        label,
                        "similarity":   round(score, 3),
                        "meaning":      neuron.data.get(
                                            "english", "unknown"
                                        ),
                        "telugu":       neuron.data.get("telugu", ""),
                        "language":     neuron.language,
                        "neuron_type":  neuron.neuron_type.value,
                        "strength":     round(neuron.strength, 3),
                        "confirmed":    neuron.confirmed_by_user,
                    })

        # Also check suffix-stripped versions
        stripped_matches = self._match_by_suffix_stripping(
            unknown_word, min_similarity
        )
        matches.extend(stripped_matches)

        # Deduplicate and sort
        seen   = set()
        unique = []
        for m in matches:
            if m["label"] not in seen:
                seen.add(m["label"])
                unique.append(m)

        unique.sort(key=lambda x: x["similarity"], reverse=True)
        return unique[:top_n]

    def _match_by_suffix_stripping(
        self, word: str, min_sim: float
    ) -> list[dict]:
        """
        Telugu words are built with suffixes.
        Try removing common endings to find the root.

        "chestunnav" → strip "av" → "chestunna" → known!
        "bagunnanu"  → strip "nu" → "bagunna"  → known!
        """
        common_suffixes = [
            "nu", "av", "aru", "adu", "di",
            "lu", "ni", "ki", "lo", "tho",
            "aa", "te", "le", "na", "ne",
            "am", "em", "indi", "undi"
        ]

        matches = []
        for suffix in common_suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                root = word[:-len(suffix)]

                # Check if root is in brain
                neuron_id = self.brain._label_index.get(root)
                if neuron_id:
                    neuron = self.brain._neurons[neuron_id]
                    matches.append({
                        "label":        root,
                        "similarity":   0.75,
                        "meaning":      neuron.data.get("english", ""),
                        "telugu":       neuron.data.get("telugu", ""),
                        "language":     neuron.language,
                        "neuron_type":  neuron.neuron_type.value,
                        "strength":     neuron.strength,
                        "confirmed":    neuron.confirmed_by_user,
                        "note":         f"Found by stripping suffix '-{suffix}'"
                    })

        return matches

    def suggest_spelling(
        self, word: str, top_n: int = 3
    ) -> list[str]:
        """
        Did the user misspell a Tenglish word?
        Suggest closest known words.
        """
        similar = self.find_similar(word, top_n=top_n, min_similarity=0.6)
        return [m["label"] for m in similar]
