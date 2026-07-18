"""
═══════════════════════════════════════════════════════
SYNAPSE — The connection between two neurons.
This is where the intelligence lives.
Not in individual neurons — in HOW they connect.

"chala" → "bagundi"   weight=0.9  (always together)
"chala" → "kastam"    weight=0.4  (sometimes together)
"chala" → "boring"    weight=0.1  (rarely together)

Hebbian Rule: "Neurons that fire together, wire together"
══════════════════════════════════════════════════════
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class SynapseType(Enum):
    """What KIND of relationship connects two neurons?"""

    # Language relationships
    MEANS_SAME_AS   = "means_same_as"      # chala ↔ bahut (both = very)
    TRANSLATES_TO   = "translates_to"      # chala → "very much"
    OPPOSITE_OF     = "opposite_of"        # bagundi ↔ chedduga
    PART_OF         = "part_of"            # "cha" is part of "chala"
    VARIANT_OF      = "variant_of"         # "neku" is variant of "neeku"

    # Usage relationships
    USED_WITH       = "used_with"          # chala + bagundi (co-occurrence)
    FOLLOWS         = "follows"            # "chala" often followed by adjective
    PRECEDES        = "precedes"           # adjective often precedes "undi"
    MODIFIES        = "modifies"           # chala modifies bagundi

    # Conceptual relationships
    CAUSES          = "causes"             # loneliness → sadness
    IS_A            = "is_a"              # bagundi is_a positive_emotion
    HAS_PROPERTY    = "has_property"       # Telugu has_property agglutinative
    BELONGS_TO      = "belongs_to"         # chala belongs_to telugu

    # Memory relationships
    TRIGGERS        = "triggers"           # "okkate" triggers "loneliness" emotion
    REMINDS_OF      = "reminds_of"         # episodic association
    CO_OCCURRED     = "co_occurred"        # appeared in same conversation


@dataclass
class Synapse:
    """
    A weighted, directional connection between two neurons.
    Weight grows when both neurons fire together.
    Weight decays when connection is unused.
    """

    # ── Identity ──────────────────────────────────────────
    id:             str = field(default_factory=lambda: str(uuid.uuid4()))
    from_neuron_id: str = ""    # Source neuron
    to_neuron_id:   str = ""    # Target neuron

    # ── Relationship ──────────────────────────────────────
    synapse_type:   SynapseType = SynapseType.CO_OCCURRED
    weight:         float       = 0.1   # 0.0 (dead) → 1.0 (superhighway)

    # ── Learning Stats ────────────────────────────────────
    activation_count:   int     = 0     # How many times both fired together
    reinforcement_count: int    = 0     # How many times user confirmed link
    last_activated:     str     = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    created_at:         str     = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # ── Metadata ──────────────────────────────────────────
    bidirectional:  bool    = False  # Does it go both ways?
    context:        str     = ""     # When does this connection apply?
    notes:          str     = ""     # Why does this connection exist?

    # ══════════════════════════════════════════════════════
    # METHODS
    # ══════════════════════════════════════════════════════

    def strengthen(self, amount: float = 0.05):
        """
        Both connected neurons fired together →
        Strengthen this synapse (Hebbian learning).
        "The road between two cities gets better
         the more people travel it."
        """
        self.weight = min(1.0, self.weight + amount)
        self.activation_count += 1
        self.last_activated = datetime.now().isoformat()

    def weaken(self, amount: float = 0.02):
        """
        Connection not used → gradually weaken.
        Like a path through grass that disappears
        if nobody walks it.
        """
        self.weight = max(0.0, self.weight - amount)

    def reinforce(self, amount: float = 0.15):
        """
        User explicitly confirmed this connection is valid.
        Bigger boost than just co-occurrence.
        """
        self.weight = min(1.0, self.weight + amount)
        self.reinforcement_count += 1
        self.activation_count += 1
        self.last_activated = datetime.now().isoformat()

    def is_strong(self) -> bool:
        """Is this a strong, reliable connection?"""
        return self.weight > 0.6

    def is_dead(self) -> bool:
        """Has this connection faded away?"""
        return self.weight < 0.05

    def to_dict(self) -> dict:
        return {
            "id":                   self.id,
            "from_neuron_id":       self.from_neuron_id,
            "to_neuron_id":         self.to_neuron_id,
            "synapse_type":         self.synapse_type.value,
            "weight":               self.weight,
            "activation_count":     self.activation_count,
            "reinforcement_count":  self.reinforcement_count,
            "last_activated":       self.last_activated,
            "created_at":           self.created_at,
            "bidirectional":        self.bidirectional,
            "context":              self.context,
            "notes":                self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Synapse":
        s = cls()
        s.id                    = d["id"]
        s.from_neuron_id        = d["from_neuron_id"]
        s.to_neuron_id          = d["to_neuron_id"]
        s.synapse_type          = SynapseType(d["synapse_type"])
        s.weight                = d["weight"]
        s.activation_count      = d["activation_count"]
        s.reinforcement_count   = d["reinforcement_count"]
        s.last_activated        = d["last_activated"]
        s.created_at            = d["created_at"]
        s.bidirectional         = d["bidirectional"]
        s.context               = d["context"]
        s.notes                 = d["notes"]
        return s
