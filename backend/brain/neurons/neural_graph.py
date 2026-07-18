"""
═══════════════════════════════════════════════════════
NEURAL GRAPH — JARVIS's entire brain.
A living, growing graph of neurons and synapses.

This IS the brain.
Not stored in rows and columns.
Stored as a WEB of connected knowledge,
just like 86 billion neurons in a human brain.
═══════════════════════════════════════════════════════
"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime

import networkx as nx

from .neuron  import Neuron,  NeuronType,  MemoryLayer
from .synapse import Synapse, SynapseType


class NeuralGraph:
    """
    JARVIS's brain as a directed weighted graph.

    Nodes = Neurons (knowledge units)
    Edges = Synapses (weighted connections)

    Growing smarter with every conversation.
    """

    BRAIN_FILE = Path("jarvis_brain/neural_graph.json")

    def __init__(self):
        # NetworkX DiGraph — directed (A→B not same as B→A)
        self.graph = nx.DiGraph()

        # Fast lookup maps
        self._neurons:  dict[str, Neuron]  = {}  # id → Neuron
        self._synapses: dict[str, Synapse] = {}  # id → Synapse
        self._label_index: dict[str, str]  = {}  # label → neuron id

        # Load existing brain from disk
        self._load()

        # Seed with basic knowledge if brand new
        if len(self._neurons) == 0:
            self._seed_initial_knowledge()

    # ════════════════════════════════════════════════════
    # NEURON OPERATIONS
    # ════════════════════════════════════════════════════

    def add_neuron(self, neuron: Neuron) -> Neuron:
        """
        Add a new neuron to the brain.
        If it already exists → return existing one.
        """
        # Check if we already know this concept
        existing_id = self._label_index.get(neuron.label.lower())
        if existing_id:
            existing = self._neurons[existing_id]
            existing.fire()  # We thought about it again
            return existing

        # New neuron
        self._neurons[neuron.id] = neuron
        self._label_index[neuron.label.lower()] = neuron.id

        # Add to NetworkX graph
        self.graph.add_node(
            neuron.id,
            label=neuron.label,
            neuron_type=neuron.neuron_type.value,
            strength=neuron.strength,
            layer=neuron.memory_layer.value
        )

        self._save()
        return neuron

    def get_neuron(self, label: str) -> Optional[Neuron]:
        """Find a neuron by its label/word"""
        neuron_id = self._label_index.get(label.lower())
        if neuron_id:
            neuron = self._neurons[neuron_id]
            neuron.fire()
            return neuron
        return None

    def get_or_create_neuron(
        self,
        label:       str,
        neuron_type: NeuronType = NeuronType.CONCEPT,
        data:        dict       = None,
        language:    str        = "unknown"
    ) -> Neuron:
        """Find existing neuron OR create new one"""
        existing = self.get_neuron(label)
        if existing:
            return existing

        neuron = Neuron(
            label       = label,
            neuron_type = neuron_type,
            data        = data or {},
            language    = language
        )
        return self.add_neuron(neuron)

    def fire_neuron(self, label: str):
        """Activate a neuron — strengthens it"""
        neuron = self.get_neuron(label)
        if neuron:
            neuron.fire()
            self.graph.nodes[neuron.id]["strength"] = neuron.strength

    # ════════════════════════════════════════════════════
    # SYNAPSE OPERATIONS
    # ════════════════════════════════════════════════════

    def connect(
        self,
        from_label:     str,
        to_label:       str,
        synapse_type:   SynapseType = SynapseType.CO_OCCURRED,
        bidirectional:  bool        = False,
        context:        str         = "",
        initial_weight: float       = 0.1
    ) -> Synapse:
        """
        Create or strengthen a synapse between two neurons.
        If connection exists → strengthen it (Hebbian).
        If new → create with initial weight.
        """
        # Get or create both neurons
        from_neuron = self.get_or_create_neuron(from_label)
        to_neuron   = self.get_or_create_neuron(to_label)

        # Check if synapse already exists
        existing_synapse = self._get_synapse(
            from_neuron.id, to_neuron.id, synapse_type
        )

        if existing_synapse:
            # HEBBIAN LEARNING: strengthen existing connection
            existing_synapse.strengthen()
            self.graph[from_neuron.id][to_neuron.id]["weight"] = (
                existing_synapse.weight
            )
            return existing_synapse

        # Create new synapse
        synapse = Synapse(
            from_neuron_id  = from_neuron.id,
            to_neuron_id    = to_neuron.id,
            synapse_type    = synapse_type,
            weight          = initial_weight,
            bidirectional   = bidirectional,
            context         = context
        )

        self._synapses[synapse.id] = synapse

        # Add to NetworkX
        self.graph.add_edge(
            from_neuron.id,
            to_neuron.id,
            synapse_id      = synapse.id,
            synapse_type    = synapse_type.value,
            weight          = synapse.weight
        )

        # If bidirectional, add reverse too
        if bidirectional:
            reverse = Synapse(
                from_neuron_id  = to_neuron.id,
                to_neuron_id    = from_neuron.id,
                synapse_type    = synapse_type,
                weight          = initial_weight,
                bidirectional   = True,
                context         = context
            )
            self._synapses[reverse.id] = reverse
            self.graph.add_edge(
                to_neuron.id,
                from_neuron.id,
                synapse_id   = reverse.id,
                synapse_type = synapse_type.value,
                weight       = reverse.weight
            )

        self._save()
        return synapse

    def _get_synapse(
        self,
        from_id: str,
        to_id:   str,
        stype:   SynapseType
    ) -> Optional[Synapse]:
        """Check if a synapse between two neurons exists"""
        if self.graph.has_edge(from_id, to_id):
            edge_data = self.graph[from_id][to_id]
            synapse_id = edge_data.get("synapse_id")
            if synapse_id and synapse_id in self._synapses:
                s = self._synapses[synapse_id]
                if s.synapse_type == stype:
                    return s
        return None

    # ════════════════════════════════════════════════════
    # ASSOCIATIVE RECALL — The magic of linked memory
    # ════════════════════════════════════════════════════

    def recall_associations(
        self,
        label:          str,
        depth:          int   = 2,
        min_weight:     float = 0.1,
        max_results:    int   = 10
    ) -> list[dict]:
        """
        Given one concept → find everything connected to it.
        Like when you think "chala" and your brain immediately
        recalls "bagundi", "kastam", "Telugu", "intensifier"...

        depth=1: direct connections only
        depth=2: connections of connections (how humans think)
        """
        start_neuron = self.get_neuron(label)
        if not start_neuron:
            return []

        associated = []

        # BFS through the graph up to given depth
        visited = {start_neuron.id}
        queue   = [(start_neuron.id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_depth >= depth:
                continue

            # Get all neighbors
            for neighbor_id in self.graph.successors(current_id):
                if neighbor_id in visited:
                    continue

                edge = self.graph[current_id][neighbor_id]
                weight = edge.get("weight", 0)

                if weight < min_weight:
                    continue

                neighbor = self._neurons.get(neighbor_id)
                if not neighbor:
                    continue

                associated.append({
                    "label":        neighbor.label,
                    "type":         neighbor.neuron_type.value,
                    "connection":   edge.get("synapse_type", "unknown"),
                    "weight":       round(weight, 3),
                    "depth":        current_depth + 1,
                    "data":         neighbor.data,
                    "strength":     round(neighbor.strength, 3)
                })

                visited.add(neighbor_id)
                queue.append((neighbor_id, current_depth + 1))

        # Sort by weight (strongest connections first)
        associated.sort(key=lambda x: x["weight"], reverse=True)
        return associated[:max_results]

    def find_path(
        self, from_label: str, to_label: str
    ) -> list[str]:
        """
        Find the neural pathway between two concepts.
        Like how 'chala' connects to 'English' through
        'telugu' → 'language' → 'English'
        """
        from_neuron = self.get_neuron(from_label)
        to_neuron   = self.get_neuron(to_label)

        if not from_neuron or not to_neuron:
            return []

        try:
            path_ids = nx.shortest_path(
                self.graph,
                from_neuron.id,
                to_neuron.id,
                weight=lambda u, v, d: 1 - d.get("weight", 0.1)
            )
            # Convert IDs back to labels
            return [
                self._neurons[nid].label
                for nid in path_ids
                if nid in self._neurons
            ]
        except nx.NetworkXNoPath:
            return []

    def get_strongest_connections(
        self, label: str, top_n: int = 5
    ) -> list[dict]:
        """
        What are the strongest neural pathways FROM this concept?
        These are the most automatic associations.
        """
        neuron = self.get_neuron(label)
        if not neuron:
            return []

        connections = []
        for neighbor_id in self.graph.successors(neuron.id):
            edge = self.graph[neuron.id][neighbor_id]
            neighbor = self._neurons.get(neighbor_id)
            if neighbor:
                connections.append({
                    "to":           neighbor.label,
                    "weight":       edge.get("weight", 0),
                    "type":         edge.get("synapse_type", "?"),
                    "activations":  self._synapses.get(
                        edge.get("synapse_id", ""), Synapse()
                    ).activation_count
                })

        connections.sort(key=lambda x: x["weight"], reverse=True)
        return connections[:top_n]

    # ════════════════════════════════════════════════════
    # RELATIONSHIP INTELLIGENCE
    # ════════════════════════════════════════════════════

    def update_person_relationship(
        self, 
        name: str, 
        duration_delta: int = 0, 
        sentiment_score: float = 0.0,
        dialect_register: str = "General"
    ):
        """
        Updates the 'closeness' of a person node.
        Logic: longer calls and informal registers increase closeness.
        """
        person = self.get_or_create_neuron(name, neuron_type=NeuronType.PERSON)
        
        # Initialize person data if empty
        if "closeness_index" not in person.data:
            person.data.update({
                "closeness_index": 0.1,
                "total_call_duration": 0,
                "sentiment_history": [],
                "preferred_dialect": dialect_register
            })
            
        # Update metrics
        person.data["total_call_duration"] += duration_delta
        person.data["closeness_index"] = min(1.0, person.data["closeness_index"] + (duration_delta / 36000))
        
        if sentiment_score != 0:
            person.data["sentiment_history"].append(sentiment_score)
            if len(person.data["sentiment_history"]) > 10:
                person.data["sentiment_history"].pop(0)
                
        person.fire(boost=0.02)
        self._save()
        logger.info(f"[Graph] Relationship updated for {name}: Closeness {person.data['closeness_index']:.2f}")

    # ════════════════════════════════════════════════════
    # BRAIN STATS
    # ════════════════════════════════════════════════════

    def get_brain_stats(self) -> dict:
        """How developed is JARVIS's brain right now?"""
        total_neurons   = len(self._neurons)
        total_synapses  = len(self._synapses)

        ltm_neurons = sum(
            1 for n in self._neurons.values()
            if n.memory_layer == MemoryLayer.LONG_TERM
        )
        confirmed = sum(
            1 for n in self._neurons.values()
            if n.confirmed_by_user
        )

        strong_synapses = sum(
            1 for s in self._synapses.values()
            if s.weight > 0.6
        )

        by_language: dict[str, int] = {}
        for n in self._neurons.values():
            lang = n.language
            by_language[lang] = by_language.get(lang, 0) + 1

        return {
            "total_neurons":    total_neurons,
            "total_synapses":   total_synapses,
            "ltm_neurons":      ltm_neurons,
            "stm_neurons":      total_neurons - ltm_neurons,
            "confirmed_facts":  confirmed,
            "strong_pathways":  strong_synapses,
            "neurons_by_language": by_language,
            "brain_density":    round(
                total_synapses / max(total_neurons, 1), 2
            ),
            "avg_neuron_strength": round(
                sum(n.strength for n in self._neurons.values())
                / max(total_neurons, 1), 3
            )
        }

    # ════════════════════════════════════════════════════
    # PERSISTENCE — Save and Load the brain
    # ════════════════════════════════════════════════════

    def _save(self):
        """Persist the entire brain to disk"""
        self.BRAIN_FILE.parent.mkdir(parents=True, exist_ok=True)

        brain_data = {
            "saved_at": datetime.now().isoformat(),
            "neurons":  [n.to_dict() for n in self._neurons.values()],
            "synapses": [s.to_dict() for s in self._synapses.values()],
        }

        self.BRAIN_FILE.write_text(
            json.dumps(brain_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _load(self):
        """Load the brain from disk"""
        if not self.BRAIN_FILE.exists():
            return

        try:
            data = json.loads(
                self.BRAIN_FILE.read_text(encoding="utf-8")
            )

            for n_data in data.get("neurons", []):
                neuron = Neuron.from_dict(n_data)
                self._neurons[neuron.id] = neuron
                self._label_index[neuron.label.lower()] = neuron.id
                self.graph.add_node(
                    neuron.id,
                    label       = neuron.label,
                    strength    = neuron.strength,
                    neuron_type = neuron.neuron_type.value
                )

            for s_data in data.get("synapses", []):
                synapse = Synapse.from_dict(s_data)
                self._synapses[synapse.id] = synapse
                self.graph.add_edge(
                    synapse.from_neuron_id,
                    synapse.to_neuron_id,
                    synapse_id   = synapse.id,
                    synapse_type = synapse.synapse_type.value,
                    weight       = synapse.weight
                )

            print(f"Brain loaded: {len(self._neurons)} neurons, "
                  f"{len(self._synapses)} synapses")

        except Exception as e:
            print(f"Brain load error: {e}")

    # ════════════════════════════════════════════════════
    # SEED KNOWLEDGE — Pre-wire basic connections
    # ════════════════════════════════════════════════════

    def _seed_initial_knowledge(self):
        """
        Give JARVIS a starter brain — like a baby
        who already knows some basic patterns.
        Pre-wire the most obvious connections.
        """
        print("Seeding initial brain knowledge...")

        # ── Seed Telugu language neurons ────────────────
        telugu_words = [
            ("chala",      NeuronType.WORD,    "telugu",
             {"english": "very much", "telugu": "చాలా", "hindi": "बहुत"}),
            ("bagundi",    NeuronType.WORD,    "telugu",
             {"english": "good/it is good", "telugu": "బాగుంది"}),
            ("naku",       NeuronType.WORD,    "telugu",
             {"english": "to me/I feel", "telugu": "నాకు"}),
            ("em",         NeuronType.WORD,    "telugu",
             {"english": "what", "telugu": "ఏం"}),
            ("telugu",     NeuronType.LANGUAGE, "telugu",
             {"family": "Dravidian", "script": "Telugu script"}),
            ("hindi",      NeuronType.LANGUAGE, "hindi",
             {"family": "Indo-Aryan", "script": "Devanagari"}),
            ("happiness",  NeuronType.EMOTION,  "universal",
             {"valence": "positive", "intensity": 0.8}),
            ("sadness",    NeuronType.EMOTION,  "universal",
             {"valence": "negative", "intensity": 0.7}),
            ("loneliness", NeuronType.EMOTION,  "universal",
             {"valence": "negative", "intensity": 0.6}),
        ]

        for label, n_type, lang, data in telugu_words:
            n = Neuron(
                label       = label,
                neuron_type = n_type,
                language    = lang,
                data        = data,
                strength    = 0.8,
                memory_layer= MemoryLayer.LONG_TERM,
                confirmed_by_user = True
            )
            self.add_neuron(n)

        # ── Pre-wire obvious connections ────────────────
        # "chala" + "bagundi" always go together
        self.connect(
            "chala", "bagundi",
            SynapseType.USED_WITH,
            bidirectional=True,
            initial_weight=0.8
        )

        # "chala" belongs to Telugu
        self.connect(
            "chala", "telugu",
            SynapseType.BELONGS_TO,
            initial_weight=0.9
        )

        # "chala" means "very much" (links to concept)
        self.connect(
            "chala", "happiness",
            SynapseType.TRIGGERS,
            initial_weight=0.3
        )

        # "bagundi" triggers happiness emotion
        self.connect(
            "bagundi", "happiness",
            SynapseType.TRIGGERS,
            initial_weight=0.7
        )

        # ── Seed Owner Person ───────────────────────────
        self.get_or_create_neuron(
            "Owner", 
            neuron_type=NeuronType.PERSON, 
            data={"role": "Boss", "closeness_index": 1.0}
        )

        print(f"Brain seeded with {len(self._neurons)} neurons")
        self._save()
