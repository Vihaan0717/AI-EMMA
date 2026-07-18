"""
═══════════════════════════════════════════════════════════════
WORD CONSTRUCTOR AGENT
The main coordinator — takes any unknown word
and runs the full analysis pipeline.

Usage in conversation:
  User: "chestunnanu ante em?"
  Agent: Detects "chestunnanu" as unknown
       → Decomposes: che(do) + stunna(present) + nu(I)
       → Constructs: "I am doing"
       → Asks: "Boss, chestunnanu = 'I am doing' — correct aa?"
  User: "avunu correct"
       → Saves to LTM forever
       → Wires to che, stunna, nu neurons
       → Brain grows 💪
═══════════════════════════════════════════════════════════════
"""

import re
from brain.neurons        import JARVISBrain
from .morpheme_engine     import MorphemeEngine
from .phonetic_matcher    import PhoneticMatcher
from .meaning_assembler   import MeaningAssembler
from .feedback_loop       import FeedbackLoop


class WordConstructorAgent:
    """
    The complete word construction and learning agent.
    Plug this into main.py to make JARVIS learn
    any Telugu/Tenglish/Hindi word it encounters.
    """

    def __init__(self, brain: JARVISBrain):
        self.brain     = brain.graph           # NeuralGraph
        self.learner   = brain.learner         # HebbianLearner
        self.assembler = MeaningAssembler(brain.graph)
        self.feedback  = FeedbackLoop(brain.graph)

        # Track what we're currently analyzing per user
        self._active_analysis: dict[str, dict] = {}

    # ════════════════════════════════════════════════════
    # MAIN ENTRY: Analyze a full message
    # ════════════════════════════════════════════════════

    def analyze_message(
        self,
        message: str,
        context: dict = None,
        user_id: str  = "boss"
    ) -> dict:
        """
        Scan a full message → find unknown words →
        construct meanings → ask for confirmation.

        Returns:
        {
            "unknown_words": [...],
            "constructed":   [...],
            "questions":     [...],
            "all_known":     True/False
        }
        """
        context = context or {}
        words   = self._extract_words(message)

        result = {
            "unknown_words":    [],
            "constructed":      [],
            "questions":        [],
            "all_known":        True
        }

        for word in words:
            if len(word) < 2:
                continue

            # Check if brain knows this word
            neuron = self.brain.get_neuron(word)
            if neuron and neuron.confirmed_by_user:
                continue  # Already known, skip

            # Unknown word — analyze it
            assembled = self.assembler.assemble(
                word    = word,
                context = {
                    **context,
                    "surrounding_words": [
                        w for w in words if w != word
                    ]
                }
            )

            result["unknown_words"].append(word)
            result["all_known"] = False

            construction = {
                "word":             word,
                "constructed_meaning": assembled.constructed_meaning,
                "confidence":       assembled.confidence,
                "morphemes":        assembled.morpheme_breakdown,
                "phonetic_matches": assembled.phonetic_matches[:3],
                "sources":          assembled.sources,
            }
            result["constructed"].append(construction)

            # Store pending confirmation
            if assembled.ready_to_confirm:
                question = self.feedback.submit_for_confirmation(
                    assembled, user_id
                )
                result["questions"].append({
                    "word":     word,
                    "question": question,
                    "confidence": assembled.confidence
                })

                # Store as active analysis
                self._active_analysis[f"{user_id}:{word}"] = {
                    "assembled": assembled,
                    "word":      word
                }

        return result

    # ════════════════════════════════════════════════════
    # ANALYZE A SINGLE WORD
    # ════════════════════════════════════════════════════

    def analyze_word(
        self,
        word:    str,
        context: dict = None,
        user_id: str  = "boss"
    ) -> dict:
        """
        Deep analysis of one specific word.
        Returns everything JARVIS knows/infers about it.
        """
        context  = context or {}
        word     = word.lower().strip()

        # ── Check if already known ────────────────────────
        existing_neuron = self.brain.get_neuron(word)

        if existing_neuron and existing_neuron.confirmed_by_user:
            return {
                "status":    "known",
                "word":      word,
                "meaning":   existing_neuron.data.get("english", ""),
                "telugu":    existing_neuron.data.get("telugu", ""),
                "hindi":     existing_neuron.data.get("hindi", ""),
                "grammar":   existing_neuron.data.get("grammar", ""),
                "strength":  existing_neuron.strength,
                "times_recalled": existing_neuron.activation_count,
                "associations": self.brain.recall_associations(
                    word, depth=2
                ),
                "message":   (
                    f"✅ Boss, '{word}' naku telusa!\n"
                    f"Meaning: {existing_neuron.data.get('english')}\n"
                    f"Telugu: {existing_neuron.data.get('telugu', '—')}"
                )
            }

        # ── Full analysis for unknown word ────────────────
        assembled = self.assembler.assemble(word, context)

        # Format detailed breakdown for display
        breakdown_display = self._format_breakdown(assembled)

        # Store for feedback
        question = self.feedback.submit_for_confirmation(
            assembled, user_id
        )
        self._active_analysis[f"{user_id}:{word}"] = {
            "assembled": assembled,
            "word":      word
        }

        return {
            "status":           "analyzed",
            "word":             word,
            "constructed_meaning": assembled.constructed_meaning,
            "confidence":       assembled.confidence,
            "confidence_label": self._confidence_label(
                assembled.confidence
            ),
            "morphemes":        assembled.morpheme_breakdown,
            "phonetic_matches": assembled.phonetic_matches,
            "neural_associations": assembled.neural_associations,
            "sources":          assembled.sources,
            "breakdown_display": breakdown_display,
            "question":         question,
            "message":          question
        }

    # ════════════════════════════════════════════════════
    # HELPER METHODS
    # ════════════════════════════════════════════════════

    def _extract_words(self, text: str) -> list[str]:
        """Extract individual words from a sentence"""
        return re.findall(r'\b[a-zA-Z\u0C00-\u0C7F\u0900-\u097F]+\b', text)

    def _confidence_label(self, score: float) -> str:
        """Convert score to human-readable label"""
        if score >= 0.8: return "High (Confident)"
        if score >= 0.5: return "Medium (Likely)"
        if score >= 0.2: return "Low (Guessing)"
        return "Minimal (Unknown)"

    def _format_breakdown(self, assembled) -> str:
        """Format the morpheme breakdown for user display"""
        parts = []
        for m in assembled.morpheme_breakdown:
            status = "✅" if m["known"] else "❓"
            parts.append(f"{status} {m['part']} ({m['meaning']})")
        
        return " | ".join(parts)

    def process_feedback(
        self,
        word: str,
        is_correct: bool,
        correction: str = None,
        user_id: str = "boss"
    ) -> dict:
        """Process user's yes/no feedback on a construction"""
        if is_correct:
            return self.feedback.confirm(word, user_id)
        else:
            if correction:
                return self.feedback.correct(word, correction, user_id)
            else:
                return {
                    "success": False,
                    "message": "Boss, please tell me the correct meaning if I was wrong!"
                }
