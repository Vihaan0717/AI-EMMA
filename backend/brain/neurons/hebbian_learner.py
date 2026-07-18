"""
═══════════════════════════════════════════════════════
HEBBIAN LEARNER
"Neurons that fire together, wire together."
— Donald Hebb, 1949

This is the core learning mechanism.
Every conversation → JARVIS finds which neurons
fired together → strengthens those connections.
═══════════════════════════════════════════════════════
"""

import re
from .neural_graph import NeuralGraph
from .neuron       import Neuron, NeuronType, MemoryLayer
from .synapse      import SynapseType


class HebbianLearner:
    """
    Processes every message → extracts concepts →
    fires those neurons → wires them together.
    """

    def __init__(self, brain: NeuralGraph):
        self.brain = brain

    def process_message(
        self,
        message:  str,
        response: str,
        context:  dict = None
    ) -> dict:
        """
        Full learning cycle for one conversation turn.

        1. Extract concepts from message
        2. Fire those neurons (strengthen them)
        3. Connect co-occurring concepts (Hebbian)
        4. Tag with emotion
        5. Store episode
        6. Return what was learned
        """
        context = context or {}
        learned = {
            "neurons_fired":    [],
            "synapses_formed":  [],
            "synapses_strengthened": [],
            "new_concepts":     []
        }

        # ── Step 1: Extract all concepts from message ───
        concepts = self._extract_concepts(message, context)

        # ── Step 2: Fire each concept neuron ────────────
        fired_neurons = []
        for concept in concepts:
            neuron = self.brain.get_or_create_neuron(
                label       = concept["label"],
                neuron_type = concept["type"],
                data        = concept["data"],
                language    = concept.get("language", "unknown")
            )
            neuron.fire()
            fired_neurons.append(neuron)
            learned["neurons_fired"].append(neuron.label)

            if neuron.activation_count == 1:
                learned["new_concepts"].append(neuron.label)

        # ── Step 3: Wire co-occurring neurons together ──
        # Every pair that appeared in same message gets connected
        for i, n1 in enumerate(fired_neurons):
            for n2 in fired_neurons[i+1:]:
                if n1.id == n2.id:
                    continue

                synapse = self.brain.connect(
                    from_label      = n1.label,
                    to_label        = n2.label,
                    synapse_type    = SynapseType.CO_OCCURRED,
                    bidirectional   = True,
                    context         = message[:100]
                )

                if synapse.activation_count > 1:
                    learned["synapses_strengthened"].append(
                        f"{n1.label} <-> {n2.label} "
                        f"(weight: {synapse.weight:.2f})"
                    )
                else:
                    learned["synapses_formed"].append(
                        f"{n1.label} <-> {n2.label}"
                    )

        # ── Step 4: Sequential connections (word order) ──
        # Words that appear IN SEQUENCE have directional link
        for i in range(len(fired_neurons) - 1):
            self.brain.connect(
                from_label   = fired_neurons[i].label,
                to_label     = fired_neurons[i+1].label,
                synapse_type = SynapseType.FOLLOWS,
                initial_weight = 0.05
            )

        # ── Step 5: Tag with emotion if detected ────────
        emotion = context.get("emotion", "neutral")
        if emotion != "neutral":
            emotion_neuron = self.brain.get_or_create_neuron(
                label       = emotion,
                neuron_type = NeuronType.EMOTION,
                language    = "universal"
            )
            for neuron in fired_neurons:
                self.brain.connect(
                    from_label   = neuron.label,
                    to_label     = emotion,
                    synapse_type = SynapseType.TRIGGERS,
                    initial_weight = 0.1
                )

        # ── Step 6: Store episode memory ─────────────────
        episode = Neuron(
            label       = f"episode_{len(self.brain._neurons)}",
            neuron_type = NeuronType.EPISODE,
            memory_layer= MemoryLayer.SHORT_TERM,
            language    = context.get("language", "unknown"),
            data = {
                "user_said":    message,
                "jarvis_said":  response,
                "concepts":     [n.label for n in fired_neurons],
                "emotion":      emotion,
            }
        )
        self.brain.add_neuron(episode)

        # Connect episode to all concepts it contains
        for neuron in fired_neurons:
            self.brain.connect(
                from_label   = episode.label,
                to_label     = neuron.label,
                synapse_type = SynapseType.CO_OCCURRED,
                initial_weight = 0.3
            )

        self.brain._save()
        return learned

    def apply_feedback(self, interaction_data: dict, score: float):
        """
        Adjusts synapse weights based on user feedback.
        If score > 0.8, we strengthen the connections that fired.
        If score < 0.3, we weaken them.
        """
        concepts = interaction_data.get("concepts", [])
        adjustment = (score - 0.5) * 0.2 # Scale adjustment
        
        for i, c1 in enumerate(concepts):
            for c2 in concepts[i+1:]:
                synapse = self.brain.get_synapse(c1, c2)
                if synapse:
                    synapse.weight = max(0.01, min(1.0, synapse.weight + adjustment))
                    logger.info(f"Hebbian: Adjusted {c1} <-> {c2} weight to {synapse.weight:.2f}")

    def _extract_concepts(
        self, message: str, context: dict
    ) -> list[dict]:
        """
        Pull every meaningful concept from a message.
        Words, emotions, language markers, grammar patterns.
        """
        concepts = []
        words = re.findall(r'\b[a-zA-Z\u0C00-\u0C7F\u0900-\u097F]+\b',
                           message.lower())

        # Known Telugu/Tenglish word list (from lexicon)
        try:
            from brain.language.telugu_lexicon import TELUGU_LEXICON
        except ImportError:
            TELUGU_LEXICON = {}

        for word in words:
            if word in TELUGU_LEXICON:
                entry = TELUGU_LEXICON[word]
                concepts.append({
                    "label":    word,
                    "type":     NeuronType.WORD,
                    "language": "telugu",
                    "data":     entry
                })
            elif len(word) > 2:  # Skip tiny words
                concepts.append({
                    "label":    word,
                    "type":     NeuronType.WORD,
                    "language": context.get("language", "unknown"),
                    "data":     {}
                })

        # Add language as a concept
        if context.get("language"):
            concepts.append({
                "label":    context["language"],
                "type":     NeuronType.LANGUAGE,
                "language": "meta",
                "data":     {}
            })

        # Add intent as a concept
        if context.get("intent"):
            concepts.append({
                "label":    context["intent"],
                "type":     NeuronType.CONCEPT,
                "language": "meta",
                "data":     {}
            })

        return concepts
