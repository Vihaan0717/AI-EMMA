"""
═══════════════════════════════════════════════════════════════
MEANING ASSEMBLER
Takes decomposed morphemes + neural associations
and builds a confident, natural meaning.

Think of it like the brain's Wernicke's area —
the part that makes sense of language.

It combines:
  1. Morpheme meanings (from MorphemeEngine)
  2. Neural associations (from NeuralGraph)
  3. Context from current conversation
  4. Phonetic matches (from PhoneticMatcher)

Into one coherent meaning with a confidence score.
═══════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from brain.neurons.neural_graph import NeuralGraph
from .morpheme_engine import MorphemeEngine, WordDecomposition
from .phonetic_matcher import PhoneticMatcher


@dataclass
class AssembledMeaning:
    """Final constructed meaning of an unknown word"""
    word:               str
    constructed_meaning: str    = ""
    telugu_script:      str     = ""
    hindi_equivalent:   str     = ""
    grammar_role:       str     = ""
    confidence:         float   = 0.0
    sources:            list    = field(default_factory=list)
    morpheme_breakdown: list    = field(default_factory=list)
    neural_associations: list   = field(default_factory=list)
    phonetic_matches:   list    = field(default_factory=list)
    ready_to_confirm:   bool    = False
    confirmation_question: str  = ""


class MeaningAssembler:
    """
    Combines all analysis methods to build
    a confident meaning for any word.
    """

    # Confidence thresholds
    HIGH_CONFIDENCE     = 0.75  # Ready to use
    MEDIUM_CONFIDENCE   = 0.45  # Ask user to confirm
    LOW_CONFIDENCE      = 0.20  # Tell user we're guessing

    def __init__(self, brain: NeuralGraph):
        self.brain    = brain
        self.morpheme = MorphemeEngine()
        self.phonetic = PhoneticMatcher(brain)

    def assemble(
        self,
        word:    str,
        context: dict = None
    ) -> AssembledMeaning:
        """
        Full meaning construction pipeline for one word.

        Pipeline:
        1. Check if brain already knows it
        2. Morpheme decomposition
        3. Neural association search
        4. Phonetic similarity search
        5. Combine all evidence
        6. Score confidence
        7. Build confirmation question
        """
        context = context or {}
        result  = AssembledMeaning(word=word)

        # ── Step 1: Check brain directly ────────────────
        known_neuron = self.brain.get_neuron(word)
        if known_neuron and known_neuron.confirmed_by_user:
            result.constructed_meaning  = known_neuron.data.get(
                "english", "known word"
            )
            result.telugu_script        = known_neuron.data.get(
                "telugu", ""
            )
            result.hindi_equivalent     = known_neuron.data.get(
                "hindi", ""
            )
            result.grammar_role         = known_neuron.data.get(
                "grammar", ""
            )
            result.confidence           = 1.0
            result.sources.append("direct_brain_lookup")
            result.ready_to_confirm     = True
            return result

        # ── Step 2: Morpheme decomposition ──────────────
        decomposition = self.morpheme.decompose(word)
        result.morpheme_breakdown = [
            {
                "part":     m.text,
                "meaning":  m.meaning,
                "type":     m.type,
                "known":    m.is_known
            }
            for m in decomposition.morphemes
        ]

        if decomposition.constructed_meaning != "meaning unclear":
            result.constructed_meaning  = decomposition.constructed_meaning
            result.confidence           = decomposition.confidence * 0.8
            result.sources.append("morpheme_decomposition")

        # ── Step 3: Neural association search ───────────
        # Search for all morpheme parts in the brain
        all_associations = []
        for morpheme in decomposition.morphemes:
            if morpheme.is_known:
                assocs = self.brain.recall_associations(
                    morpheme.text, depth=1
                )
                all_associations.extend(assocs)

        result.neural_associations = all_associations[:8]

        # Boost confidence if strong neural evidence
        strong_assocs = [
            a for a in all_associations if a["weight"] > 0.6
        ]
        if strong_assocs:
            result.confidence = min(
                result.confidence + 0.1 * len(strong_assocs),
                0.95
            )
            result.sources.append("neural_association")

        # ── Step 4: Phonetic matching ────────────────────
        phonetic_matches = self.phonetic.find_similar(word, top_n=5)
        result.phonetic_matches = phonetic_matches

        # If phonetic match is very strong, use its meaning
        if phonetic_matches and phonetic_matches[0]["similarity"] > 0.8:
            best_phonetic = phonetic_matches[0]
            if not result.constructed_meaning:
                result.constructed_meaning = (
                    f"Similar to '{best_phonetic['label']}': "
                    f"{best_phonetic['meaning']}"
                )
                result.confidence = best_phonetic["similarity"] * 0.7
                result.sources.append("phonetic_similarity")
            else:
                result.confidence = min(
                    result.confidence + 0.1, 0.95
                )

        # ── Step 5: Context boost ────────────────────────
        # If surrounding words give us hints
        if context.get("surrounding_words"):
            context_boost = self._context_boost(
                word, context["surrounding_words"]
            )
            result.confidence = min(
                result.confidence + context_boost, 0.95
            )
            if context_boost > 0:
                result.sources.append("context_inference")

        # ── Step 6: Telugu script lookup ─────────────────
        if not result.telugu_script:
            result.telugu_script = self._guess_telugu_script(
                decomposition
            )

        # ── Step 7: Build confirmation question ──────────
        result.ready_to_confirm = (
            result.confidence >= self.MEDIUM_CONFIDENCE
        )
        result.confirmation_question = self._build_question(result)

        return result

    def _context_boost(
        self, word: str, surrounding_words: list[str]
    ) -> float:
        """
        Check if surrounding words hint at meaning.
        "naku ___ ga undi" → word is probably an emotion/state.
        """
        boost = 0.0
        emotion_contexts = {"undi", "ga", "naku", "neeku", "maku"}
        question_contexts = {"em", "ela", "evaru", "ekkada", "epudu"}

        for surr in surrounding_words:
            if surr.lower() in emotion_contexts:
                boost += 0.05
            if surr.lower() in question_contexts:
                boost += 0.03

        return boost

    def _guess_telugu_script(
        self, decomp: WordDecomposition
    ) -> str:
        """Combine Telugu scripts from morphemes"""
        parts = []
        for m in decomp.morphemes:
            if m.telugu:
                parts.append(m.telugu)
        return "".join(parts) if parts else ""

    def _build_question(self, result: AssembledMeaning) -> str:
        """Build natural confirmation question for user"""

        if result.confidence >= self.HIGH_CONFIDENCE:
            return (
                f"Boss, '{result.word}' ante "
                f"'{result.constructed_meaning}' — correct aa? ✅"
            )

        elif result.confidence >= self.MEDIUM_CONFIDENCE:
            # Show our reasoning
            sources_text = " + ".join(result.sources)
            breakdown_text = ""
            if result.morpheme_breakdown:
                known_parts = [
                    f"'{p['part']}'={p['meaning']}"
                    for p in result.morpheme_breakdown
                    if p["known"]
                ]
                if known_parts:
                    breakdown_text = (
                        f"\nParts found: {' | '.join(known_parts)}"
                    )

            return (
                f"Boss, '{result.word}' — naku exactly teliyadu, "
                f"kani nenu try chesanu:{breakdown_text}\n"
                f"Meaning: '{result.constructed_meaning}' — "
                f"idi correct aa? ✅❌"
            )

        else:
            phonetic_hint = ""
            if result.phonetic_matches:
                best = result.phonetic_matches[0]
                phonetic_hint = (
                    f"\nSimilar to '{best['label']}' "
                    f"({best['meaning']}) — maybe?"
                )

            return (
                f"Boss, '{result.word}' ante naku artham "
                f"kaaledu! 🤔{phonetic_hint}\n"
                f"Meeru cheppagalara — meaning em?"
            )
