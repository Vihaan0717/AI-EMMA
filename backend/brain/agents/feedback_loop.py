"""
═══════════════════════════════════════════════════════════════
FEEDBACK LOOP
The learning-confirmation-storage cycle.

1. JARVIS proposes a meaning
2. User confirms ✅ or corrects ❌
3. JARVIS saves confirmed meaning to LTM
4. JARVIS wires new neuron to all related neurons
5. JARVIS gets smarter — permanently

This is how the brain actually grows.
═══════════════════════════════════════════════════════════════
"""

from datetime import datetime
from brain.neurons.neural_graph import NeuralGraph
from brain.neurons.neuron       import Neuron, NeuronType, MemoryLayer
from brain.neurons.synapse      import SynapseType
from .meaning_assembler         import AssembledMeaning


class FeedbackLoop:
    """
    Manages the confirm/correct cycle and
    permanently wires confirmed knowledge into LTM.
    """

    # Track pending confirmations
    # (waiting for user's yes/no)
    _pending: dict[str, AssembledMeaning] = {}

    def __init__(self, brain: NeuralGraph):
        self.brain = brain

    # ════════════════════════════════════════════════════
    # SUBMIT FOR CONFIRMATION
    # ────────────────────────────────────────────────────

    def submit_for_confirmation(
        self,
        assembled: AssembledMeaning,
        user_id:   str = "boss"
    ) -> str:
        """
        Store the assembled meaning as pending,
        return the question to ask the user.
        """
        key = f"{user_id}:{assembled.word}"
        self._pending[key] = assembled
        return assembled.confirmation_question

    # ════════════════════════════════════════════════════
    # USER CONFIRMS ✅
    # ────────────────────────────────────────────────────

    def confirm(
        self,
        word:    str,
        user_id: str  = "boss",
        extra_info: dict = None
    ) -> dict:
        """
        User said YES — our meaning was correct.
        Save to LTM and wire all connections.
        """
        key      = f"{user_id}:{word}"
        assembled = self._pending.get(key)

        if not assembled:
            return {
                "success": False,
                "message": f"No pending confirmation for '{word}'"
            }

        extra_info = extra_info or {}

        # ── Build complete neuron data ───────────────────
        neuron_data = {
            "english":      assembled.constructed_meaning,
            "telugu":       assembled.telugu_script,
            "hindi":        assembled.hindi_equivalent,
            "grammar":      assembled.grammar_role,
            "confidence":   assembled.confidence,
            "sources":      assembled.sources,
            "confirmed_at": datetime.now().isoformat(),
            **extra_info
        }

        # ── Create/update the neuron ─────────────────────
        existing = self.brain.get_neuron(word)
        if existing:
            existing.data.update(neuron_data)
            existing.confirm()
            neuron = existing
        else:
            neuron = Neuron(
                label        = word,
                neuron_type  = NeuronType.WORD,
                memory_layer = MemoryLayer.LONG_TERM,
                data         = neuron_data,
                strength     = 0.8,
                confidence   = assembled.confidence,
                confirmed_by_user = True,
                language     = extra_info.get("language", "telugu")
            )
            self.brain.add_neuron(neuron)

        # ── Wire to morpheme parts ───────────────────────
        wired = []
        for part in assembled.morpheme_breakdown:
            if part["known"] and part["part"] != word:
                self.brain.connect(
                    from_label      = word,
                    to_label        = part["part"],
                    synapse_type    = SynapseType.PART_OF,
                    initial_weight  = 0.8
                )
                wired.append(part["part"])

        # ── Wire to phonetic matches ─────────────────────
        for match in assembled.phonetic_matches[:3]:
            if match["similarity"] > 0.6:
                self.brain.connect(
                    from_label      = word,
                    to_label        = match["label"],
                    synapse_type    = SynapseType.VARIANT_OF,
                    initial_weight  = match["similarity"] * 0.5
                )

        # ── Wire to neural associations ──────────────────
        for assoc in assembled.neural_associations[:5]:
            if assoc["weight"] > 0.3:
                self.brain.connect(
                    from_label      = word,
                    to_label        = assoc["label"],
                    synapse_type    = SynapseType.CO_OCCURRED,
                    initial_weight  = assoc["weight"] * 0.6
                )

        # ── Wire to language neuron ──────────────────────
        language = extra_info.get("language", "telugu")
        self.brain.connect(
            from_label   = word,
            to_label     = language,
            synapse_type = SynapseType.BELONGS_TO,
            initial_weight = 0.9
        )

        # ── Clean up pending ────────────────────────────
        del self._pending[key]

        # ── Save brain ───────────────────────────────────
        self.brain._save()

        return {
            "success":          True,
            "word":             word,
            "meaning":          assembled.constructed_meaning,
            "layer":            "LONG_TERM",
            "wired_to":         wired,
            "total_neurons":    len(self.brain._neurons),
            "message":          (
                f"✅ '{word}' = '{assembled.constructed_meaning}' "
                f"— LTM lo save chesanu Boss! "
                f"Nenu ippudu ee word gurthupettukunnanu forever! 🧠"
            )
        }

    # ════════════════════════════════════════════════════
    # USER CORRECTS ❌
    # ────────────────────────────────────────────────────

    def correct(
        self,
        word:            str,
        correct_meaning: str,
        user_id:         str  = "boss",
        extra_info:      dict = None
    ) -> dict:
        """
        User said NO and provided the real meaning.
        Save the CORRECT meaning and learn from the mistake.
        """
        key      = f"{user_id}:{word}"
        assembled = self._pending.get(key)
        extra_info = extra_info or {}

        wrong_meaning = (
            assembled.constructed_meaning
            if assembled else "unknown"
        )

        # ── Save correction neuron ───────────────────────
        neuron_data = {
            "english":          correct_meaning,
            "wrong_was":        wrong_meaning,
            "telugu":           extra_info.get("telugu", ""),
            "hindi":            extra_info.get("hindi", ""),
            "grammar":          extra_info.get("grammar", ""),
            "corrected_by":     user_id,
            "corrected_at":     datetime.now().isoformat(),
            "correction_count": 1,
        }

        existing = self.brain.get_neuron(word)
        if existing:
            # Track how many times we got this wrong
            old_count = existing.data.get("correction_count", 0)
            neuron_data["correction_count"] = old_count + 1
            existing.data.update(neuron_data)
            existing.confirm(neuron_data)
            neuron = existing
        else:
            neuron = Neuron(
                label             = word,
                neuron_type       = NeuronType.WORD,
                memory_layer      = MemoryLayer.LONG_TERM,
                data              = neuron_data,
                strength          = 0.9,    # Extra strong — hard-learned
                confidence        = 1.0,    # User confirmed directly
                confirmed_by_user = True,
                language          = extra_info.get("language", "telugu")
            )
            self.brain.add_neuron(neuron)

        # ── Create "do NOT confuse" synapses ─────────────
        # If we confused it with another word, mark that clearly
        if assembled and assembled.phonetic_matches:
            confused_with = assembled.phonetic_matches[0]["label"]
            self.brain.connect(
                from_label      = word,
                to_label        = confused_with,
                synapse_type    = SynapseType.OPPOSITE_OF,
                initial_weight  = 0.3,
                context=f"NOT the same as {confused_with}"
            )

        # ── Wire correctly ───────────────────────────────
        language = extra_info.get("language", "telugu")
        self.brain.connect(
            from_label   = word,
            to_label     = language,
            synapse_type = SynapseType.BELONGS_TO,
            initial_weight = 0.9
        )

        # Clean up pending
        if key in self._pending:
            del self._pending[key]

        self.brain._save()

        return {
            "success":       True,
            "word":          word,
            "correct_meaning": correct_meaning,
            "was_wrong":     wrong_meaning,
            "layer":         "LONG_TERM",
            "total_neurons": len(self.brain._neurons),
            "message":       (
                f"🙏 Thank you Boss! Nenu correct chesukunnanu.\n"
                f"'{word}' = '{correct_meaning}' — ippudu nenu "
                f"idi forever remember chestanu!\n"
                f"(Wrong gaa '{wrong_meaning}' anukunnanu — "
                f"adi wrong ante telusindi!)"
            )
        }

    # ════════════════════════════════════════════════════
    # TEACH MODE — User proactively teaches JARVIS
    # ────────────────────────────────────────────────────

    def teach(
        self,
        word:      str,
        meaning:   str,
        telugu:    str  = "",
        hindi:     str  = "",
        grammar:   str  = "",
        language:  str  = "telugu",
        user_id:   str  = "boss"
    ) -> dict:
        """
        User directly teaches JARVIS a new word
        without any prior guess needed.
        e.g. User types: "teach: pilla = kid/girl"
        """
        neuron_data = {
            "english":      meaning,
            "telugu":       telugu,
            "hindi":        hindi,
            "grammar":      grammar,
            "taught_by":    user_id,
            "taught_at":    datetime.now().isoformat(),
        }

        existing = self.brain.get_neuron(word)
        if existing:
            existing.data.update(neuron_data)
            existing.confirm(neuron_data)
            neuron = existing
        else:
            neuron = Neuron(
                label             = word,
                neuron_type       = NeuronType.WORD,
                memory_layer      = MemoryLayer.LONG_TERM,
                data              = neuron_data,
                strength          = 1.0,
                confidence        = 1.0,
                confirmed_by_user = True,
                language          = language
            )
            self.brain.add_neuron(neuron)

        # Connect to language
        self.brain.connect(
            word, language,
            SynapseType.BELONGS_TO,
            initial_weight=0.95
        )

        # If Telugu script provided, connect that too
        if telugu:
            telugu_neuron = self.brain.get_or_create_neuron(
                label       = telugu,
                neuron_type = NeuronType.WORD,
                language    = "telugu_script"
            )
            self.brain.connect(
                word, telugu,
                SynapseType.TRANSLATES_TO,
                bidirectional=True,
                initial_weight=0.95
            )

        self.brain._save()

        return {
            "success":       True,
            "word":          word,
            "meaning":       meaning,
            "neurons_total": len(self.brain._neurons),
            "message":       (
                f"🎓 Learned! '{word}' = '{meaning}'\n"
                f"LTM lo save chesanu Boss. "
                f"Mee Telugu knowledge JARVIS brain lo "
                f"forever undi! 🧠✨"
            )
        }
