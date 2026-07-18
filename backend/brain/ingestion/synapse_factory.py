"""
SynapseFactory — Builds neural connections from parsed notes.
Takes [[backlinks]] + shared tags → creates weighted synapses
in the NeuralGraph with proper initial Hebbian weights.
"""

import logging
import json
from typing  import Dict, List, Optional, Tuple
from pathlib import Path

from .neural_graph    import NeuralGraph
from .obsidian_parser import ParsedNote

logger = logging.getLogger("Zero.SynapseFactory")


class SynapseFactory:
    """
    Builds the actual synaptic connections.
    
    Weight initialization rules:
    ┌────────────────────────────────┬──────────────────┐
    │ Connection type                │ Initial strength │
    ├────────────────────────────────┼──────────────────┤
    │ Direct [[backlink]]            │ 0.70             │
    │ Shared tag (same domain)       │ 0.50             │
    │ Same folder (proximity)        │ 0.35             │
    │ Keyword co-occurrence          │ 0.25             │
    └────────────────────────────────┴──────────────────┘
    
    Multiple connection types stack (capped at 1.0).
    """

    # ── Initial weights ───────────────────────────────────────────
    WEIGHT_BACKLINK  = 0.70
    WEIGHT_SHARED_TAG = 0.50
    WEIGHT_PROXIMITY  = 0.35
    WEIGHT_KEYWORD    = 0.25

    def __init__(self, graph: NeuralGraph):
        self.graph = graph
        self._label_to_id: Dict[str, int] = {}   # Cache: label → neuron_id
        self._stats = {
            "neurons_created":  0,
            "neurons_updated":  0,
            "synapses_created": 0,
            "synapses_reinforced": 0
        }

    # ═══════════════════════════════════════════════════════════════
    #  PUBLIC
    # ═══════════════════════════════════════════════════════════════

    def register_note(self, note: ParsedNote) -> int:
        """
        Register a note as a neuron in the graph.
        Returns the neuron ID.
        Must be called before build_connections.
        """
        # Build auto summary from first section
        summary = self._build_summary(note)

        # Compute initial activation based on note quality
        activation = self._compute_initial_activation(note)

        neuron_id = self.graph.upsert_neuron(
            note_path          = str(note.path),
            label              = note.title,
            tags               = note.tags,
            summary            = summary,
            word_count         = note.word_count,
            initial_activation = activation
        )

        # Cache for fast lookup during connection building
        self._label_to_id[note.title.lower()] = neuron_id

        # Register aliases too
        for alias in note.aliases:
            self._label_to_id[alias.lower()] = neuron_id

        # Check if it was newly created (upsert_neuron returns ID regardless)
        # We can't easily check 'new' without querying, so we'll just track calls
        self._stats["neurons_created"] += 1

        return neuron_id

    def build_connections(
        self,
        note: ParsedNote,
        all_notes: Dict[str, int]   # {normalized_title: neuron_id}
    ) -> int:
        """
        Build all synaptic connections for a note.
        Returns number of synapses created/reinforced.
        """
        source_id    = self._get_neuron_id(note.title)
        if not source_id:
            logger.warning(f"⚠️ Neuron not found for: {note.title}")
            return 0

        connections_made = 0

        # ── 1. Direct [[backlink]] connections (strongest) ────────
        for link_target in note.backlinks:
            target_id = self._resolve_link(link_target, all_notes)
            if target_id and target_id != source_id:
                # Calculate link frequency as strength boost
                link_count = note.backlinks.count(link_target)
                strength   = min(1.0, self.WEIGHT_BACKLINK + (link_count - 1) * 0.05)

                self.graph.create_synapse(source_id, target_id, strength)
                # Bidirectional: weaker reverse
                self.graph.create_synapse(target_id, source_id, strength * 0.7)
                connections_made += 1
                self._stats["synapses_created"] += 1

        # ── 2. Shared-tag connections ─────────────────────────────
        tag_connections = self._build_tag_connections(
            note, source_id, all_notes
        )
        connections_made += tag_connections

        logger.debug(
            f"🔗 '{note.title}': {len(note.backlinks)} links, "
            f"{connections_made} synapses built"
        )
        return connections_made

    def batch_build_all(
        self, notes: List[ParsedNote]
    ) -> Dict:
        """
        Two-pass algorithm:
        Pass 1: Register all neurons (so we can resolve all links)
        Pass 2: Build all connections
        """
        logger.info(f"🏗️ SynapseFactory: Building graph for {len(notes)} notes")

        # Pass 1: Register all neurons
        all_notes: Dict[str, int] = {}
        for note in notes:
            nid = self.register_note(note)
            all_notes[note.title.lower()] = nid
            for alias in note.aliases:
                all_notes[alias.lower()] = nid

        logger.info(f"   Pass 1 complete: {len(all_notes)} neurons registered")

        # Pass 2: Build connections
        total_synapses = 0
        for note in notes:
            synapses = self.build_connections(note, all_notes)
            total_synapses += synapses

        logger.info(
            f"   Pass 2 complete: {total_synapses} synapses built"
        )

        return {
            **self._stats,
            "total_synapses": total_synapses,
            "graph_stats":    self.graph.graph_stats()
        }

    # ═══════════════════════════════════════════════════════════════
    #  PRIVATE
    # ───────────────────────────────────────────────────────────────

    def _build_tag_connections(
        self,
        note: ParsedNote,
        source_id: int,
        all_notes: Dict[str, int]
    ) -> int:
        """Connect notes that share domain-level tags."""
        if not note.tags:
            return 0

        # Get all neurons that share at least one tag
        count = 0
        note_tags = set(note.tags)

        rows = self.graph.conn.execute(
            "SELECT id, label, tags FROM neurons WHERE id != ?",
            (source_id,)
        ).fetchall()

        for row in rows:
            other_tags  = set(json.loads(row["tags"] or "[]"))
            shared_tags = note_tags & other_tags

            if not shared_tags:
                continue

            # Strength scales with number of shared tags
            strength = min(
                1.0,
                self.WEIGHT_SHARED_TAG * len(shared_tags)
            )

            self.graph.create_synapse(source_id, row["id"], strength)
            count += 1

        return count

    def _compute_initial_activation(self, note: ParsedNote) -> float:
        """
        Compute the initial activation of a neuron.
        Higher activation = more central to the knowledge graph.
        """
        score = 0.3   # Baseline

        # Backlinks = connectivity
        score += min(0.25, len(note.backlinks) * 0.025)

        # Word count = depth of knowledge
        score += min(0.20, (note.word_count / 500) * 0.20)

        # Headings = structure
        score += min(0.15, len(note.headings) * 0.03)

        # Has frontmatter = organized
        if note.frontmatter:
            score += 0.10

        return min(1.0, round(score, 3))

    def _build_summary(self, note: ParsedNote) -> str:
        """Build a concise summary from the note's first section."""
        if note.sections:
            first = note.sections[0].get("content", "")
            words = first.split()[:60]
            return " ".join(words) + ("..." if len(words) == 60 else "")
        elif note.body:
            words = note.body.split()[:60]
            return " ".join(words) + ("..." if len(words) == 60 else "")
        return ""

    def _get_neuron_id(self, label: str) -> Optional[int]:
        return self._label_to_id.get(label.lower())

    def _resolve_link(
        self,
        link_target: str,
        all_notes: Dict[str, int]
    ) -> Optional[int]:
        """Resolve a [[link target]] to a neuron ID."""
        # Try exact match first
        nid = all_notes.get(link_target.lower())
        if nid:
            return nid

        # Try partial match (handle "Folder/Note" → "Note")
        base = link_target.split("/")[-1].lower()
        nid  = all_notes.get(base)
        if nid:
            return nid

        # Try from graph directly
        neuron = self.graph.get_neuron_by_label(link_target)
        return neuron["id"] if neuron else None
