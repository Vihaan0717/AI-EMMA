"""
═══════════════════════════════════════════════════════
HIPPOCAMPUS — Memory Consolidation Engine

In the human brain, the hippocampus:
  → Receives new experiences (STM)
  → Replays them during sleep
  → Decides what to keep in LTM
  → Discards what is not important

JARVIS's hippocampus does the same.
Call consolidate() periodically to:
  → Promote strong STM neurons → LTM
  → Delete weak/forgotten neurons
  → Merge duplicate concepts
  → Strengthen well-confirmed knowledge
═══════════════════════════════════════════════════════
"""

from datetime import datetime, timedelta
from .neural_graph import NeuralGraph
from .neuron       import MemoryLayer


class Hippocampus:
    """
    Runs periodically to consolidate memory.
    Like 'sleeping' — the brain processes the day.
    """

    # Thresholds
    STM_TO_LTM_STRENGTH     = 0.4   # Min strength to graduate to LTM
    FORGET_THRESHOLD        = 0.05  # Below this → delete
    STM_AGE_HOURS           = 24    # STM neurons older than this → evaluate
    DECAY_RATE              = 0.01  # How fast unused neurons fade

    def __init__(self, brain: NeuralGraph):
        self.brain = brain

    def consolidate(self) -> dict:
        """
        Run the full memory consolidation cycle.
        Call this once a day / after N conversations.
        """
        report = {
            "promoted_to_ltm":  [],
            "forgotten":        [],
            "decayed":          [],
            "merged":           [],
            "total_before":     len(self.brain._neurons),
            "total_after":      0,
            "timestamp":        datetime.now().isoformat()
        }

        now = datetime.now()
        to_delete = []

        for neuron_id, neuron in list(self.brain._neurons.items()):

            # ── Skip confirmed LTM neurons ──────────────
            if (neuron.confirmed_by_user and
                    neuron.memory_layer == MemoryLayer.LONG_TERM):
                continue

            # ── Calculate neuron age ─────────────────────
            last_fired = datetime.fromisoformat(neuron.last_fired)
            hours_since_fired = (now - last_fired).total_seconds() / 3600

            # ── Decay unused neurons ─────────────────────
            if hours_since_fired > 1:
                neuron.decay(self.DECAY_RATE * (hours_since_fired / 24))
                report["decayed"].append(neuron.label)

            # ── Forget very weak, unconfirmed STM neurons ─
            if (neuron.is_forgotten() and
                    neuron.memory_layer == MemoryLayer.SHORT_TERM and
                    hours_since_fired > self.STM_AGE_HOURS):
                to_delete.append(neuron_id)
                report["forgotten"].append(neuron.label)
                continue

            # ── Promote strong STM → LTM ─────────────────
            if (neuron.memory_layer == MemoryLayer.SHORT_TERM and
                    neuron.strength >= self.STM_TO_LTM_STRENGTH):
                neuron.promote_to_ltm()
                report["promoted_to_ltm"].append(neuron.label)

        # ── Remove forgotten neurons ─────────────────────
        for neuron_id in to_delete:
            neuron = self.brain._neurons.pop(neuron_id, None)
            if neuron:
                label = neuron.label.lower()
                self.brain._label_index.pop(label, None)
                if self.brain.graph.has_node(neuron_id):
                    self.brain.graph.remove_node(neuron_id)

        # ── Decay weak synapses ───────────────────────────
        dead_synapses = []
        for syn_id, synapse in self.brain._synapses.items():
            if synapse.weight < 0.05 and synapse.reinforcement_count == 0:
                dead_synapses.append(syn_id)
            elif synapse.activation_count == 0:
                synapse.weaken(0.005)

        for syn_id in dead_synapses:
            synapse = self.brain._synapses.pop(syn_id, None)
            if synapse and self.brain.graph.has_edge(
                synapse.from_neuron_id, synapse.to_neuron_id
            ):
                self.brain.graph.remove_edge(
                    synapse.from_neuron_id, synapse.to_neuron_id
                )

        report["total_after"] = len(self.brain._neurons)
        self.brain._save()

        print(
            f"Consolidation: "
            f"+{len(report['promoted_to_ltm'])} LTM | "
            f"-{len(report['forgotten'])} forgotten | "
            f"{report['total_after']} neurons remain"
        )
        return report
