"""
═══════════════════════════════════════════════════════
JARVIS BRAIN — Complete Neural System
One import → full brain access
═══════════════════════════════════════════════════════
"""

from .neuron          import Neuron, NeuronType, MemoryLayer
from .synapse         import Synapse, SynapseType
from .neural_graph    import NeuralGraph
from .hebbian_learner import HebbianLearner
from .hippocampus     import Hippocampus


class JARVISBrain:
    """
    The complete brain. Plug this into main.py.
    One object that handles:
      → Learning from every message
      → Recalling associations
      → Consolidating memory
      → Growing smarter over time
    """

    def __init__(self):
        print("JARVIS Brain initializing...")
        self.graph      = NeuralGraph()          # The neural network
        self.learner    = HebbianLearner(self.graph)  # Learning engine
        self.memory     = Hippocampus(self.graph)     # Consolidation
        print("Brain online.")

    def learn(
        self,
        user_message:   str,
        jarvis_response: str,
        context:        dict = None
    ) -> dict:
        """
        Process a conversation → learn from it.
        Call after EVERY message exchange.
        """
        return self.learner.process_message(
            message  = user_message,
            response = jarvis_response,
            context  = context or {}
        )

    def recall(self, concept: str, depth: int = 2) -> list:
        """
        What does JARVIS know about this concept?
        Returns everything associated with it.
        """
        return self.graph.recall_associations(
            label=concept, depth=depth
        )

    def think_about(self, word: str) -> dict:
        """
        Full associative recall — like a human
        'thinking about' something. Returns:
          - direct knowledge of the word
          - strongest associations
          - neural pathway examples
          - emotional tags
        """
        neuron = self.graph.get_neuron(word)
        if not neuron:
            return {"known": False, "word": word}

        associations = self.graph.recall_associations(word, depth=2)
        strongest    = self.graph.get_strongest_connections(word)

        return {
            "known":        True,
            "word":         word,
            "data":         neuron.data,
            "strength":     neuron.strength,
            "layer":        neuron.memory_layer.value,
            "confirmed":    neuron.confirmed_by_user,
            "language":     neuron.language,
            "times_recalled": neuron.activation_count,
            "strongest_connections": strongest,
            "full_associations":     associations,
        }

    def consolidate(self) -> dict:
        """Run memory consolidation (call daily)"""
        return self.memory.consolidate()

    def stats(self) -> dict:
        """How big/strong is JARVIS's brain right now?"""
        return self.graph.get_brain_stats()


# Single instance — import this everywhere
try:
    brain = JARVISBrain()
except Exception as e:
    print(f"Failed to initialize brain: {e}")
    brain = None
