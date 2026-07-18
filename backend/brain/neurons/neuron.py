"""
═══════════════════════════════════════════════════════
NEURON — The basic unit of JARVIS's brain.
One neuron = one concept/word/emotion/event/person
Just like one brain cell holds one piece of information.
═══════════════════════════════════════════════════════
"""

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum


class NeuronType(Enum):
    """What kind of knowledge does this neuron hold?"""
    WORD        = "word"        # Language word (chala, bagundi)
    CONCEPT     = "concept"     # Abstract idea (happiness, distance)
    EMOTION     = "emotion"     # Feeling (happy, sad, angry)
    PERSON      = "person"      # Someone JARVIS knows (user, friend)
    EVENT       = "event"       # Something that happened
    LANGUAGE    = "language"    # Telugu, Hindi, English
    GRAMMAR     = "grammar"     # Grammar rule/pattern
    PHONETIC    = "phonetic"    # Sound/pronunciation
    EPISODE     = "episode"     # Memory of a conversation


class MemoryLayer(Enum):
    """Which memory layer is this neuron in?"""
    SENSORY     = "sensory"     # Just received — milliseconds
    SHORT_TERM  = "short_term"  # Working memory — minutes/hours
    LONG_TERM   = "long_term"   # Permanent memory — forever


@dataclass
class Neuron:
    """
    One unit of knowledge in JARVIS's brain.

    Properties that change over time (like real neurons):
    - strength    : grows with use, fades without
    - activations : how many times this memory was recalled
    - last_fired  : when was this last thought about
    """

    # ── Identity ──────────────────────────────────────────
    id:             str         = field(default_factory=lambda: str(uuid.uuid4()))
    label:          str         = ""        # Primary name: "chala", "happiness"
    neuron_type:    NeuronType  = NeuronType.CONCEPT
    memory_layer:   MemoryLayer = MemoryLayer.SHORT_TERM

    # ── Core Knowledge ────────────────────────────────────
    data: dict = field(default_factory=dict)
    # data can hold anything:
    # For WORD neuron:
    #   { "telugu": "చాలా", "english": "very much",
    #     "hindi": "बहुत", "grammar": "adverb",
    #     "pronunciation": "chaa-laa", "language": "telugu" }
    #
    # For EMOTION neuron:
    #   { "valence": "positive", "intensity": 0.8,
    #     "triggers": ["bagundi", "santosham"] }
    #
    # For EPISODE neuron:
    #   { "conversation": "user said chala okkate",
    #     "my_response": "arthamindi...",
    #     "date": "2025-01-17" }

    # ── Strength (Biological Analog) ──────────────────────
    strength:           float   = 0.1   # 0.0 (forgotten) → 1.0 (core memory)
    activation_count:   int     = 0     # How many times recalled
    confidence:         float   = 0.5   # How sure are we this is correct?
    confirmed_by_user:  bool    = False # Did user validate this?

    # ── Time Tracking ─────────────────────────────────────
    created_at:     str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    last_fired:     str = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    last_updated:   str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    # ── Context Tags ──────────────────────────────────────
    language:   str         = "unknown"     # telugu / hindi / english
    emotion_tag: str        = "neutral"     # what emotion is linked
    tags:       list        = field(default_factory=list)

    # ══════════════════════════════════════════════════════
    # METHODS — How neurons behave
    # ══════════════════════════════════════════════════════

    def fire(self, boost: float = 0.05):
        """
        Activate this neuron (it was recalled/used).
        Just like a brain cell firing — 
        firing strengthens it, makes it easier to recall next time.
        """
        self.activation_count += 1
        self.last_fired = datetime.now().isoformat()

        # Strengthen this neuron each time it fires
        # (like practicing a skill makes it easier)
        self.strength = min(1.0, self.strength + boost)
        self.last_updated = datetime.now().isoformat()

    def decay(self, decay_rate: float = 0.01):
        """
        Neurons weaken when not used.
        Ebbinghaus forgetting curve — 
        unused memories fade unless reinforced.
        Called periodically on inactive neurons.
        """
        self.strength = max(0.0, self.strength - decay_rate)
        self.last_updated = datetime.now().isoformat()

    def confirm(self, corrected_data: dict = None):
        """
        User validated this neuron's knowledge.
        Boosts strength significantly + marks confirmed.
        Like a teacher saying "yes, that's correct!"
        """
        self.confirmed_by_user = True
        self.confidence = min(1.0, self.confidence + 0.3)
        self.strength = min(1.0, self.strength + 0.2)
        self.memory_layer = MemoryLayer.LONG_TERM

        if corrected_data:
            self.data.update(corrected_data)

        self.last_updated = datetime.now().isoformat()

    def promote_to_ltm(self):
        """Move from short-term to long-term memory"""
        self.memory_layer = MemoryLayer.LONG_TERM
        self.strength = max(self.strength, 0.5)

    def is_forgotten(self) -> bool:
        """Has this memory faded below threshold?"""
        return self.strength < 0.05 and not self.confirmed_by_user

    def to_dict(self) -> dict:
        """Serialize for storage"""
        return {
            "id":               self.id,
            "label":            self.label,
            "neuron_type":      self.neuron_type.value,
            "memory_layer":     self.memory_layer.value,
            "data":             self.data,
            "strength":         self.strength,
            "activation_count": self.activation_count,
            "confidence":       self.confidence,
            "confirmed_by_user": self.confirmed_by_user,
            "created_at":       self.created_at,
            "last_fired":       self.last_fired,
            "last_updated":     self.last_updated,
            "language":         self.language,
            "emotion_tag":      self.emotion_tag,
            "tags":             self.tags,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Neuron":
        """Deserialize from storage"""
        n = cls()
        n.id               = d["id"]
        n.label            = d["label"]
        n.neuron_type      = NeuronType(d["neuron_type"])
        n.memory_layer     = MemoryLayer(d["memory_layer"])
        n.data             = d["data"]
        n.strength         = d["strength"]
        n.activation_count = d["activation_count"]
        n.confidence       = d["confidence"]
        n.confirmed_by_user = d["confirmed_by_user"]
        n.created_at       = d["created_at"]
        n.last_fired       = d["last_fired"]
        n.last_updated     = d["last_updated"]
        n.language         = d["language"]
        n.emotion_tag      = d["emotion_tag"]
        n.tags             = d["tags"]
        return n

    def __repr__(self):
        return (
            f"Neuron({self.label!r} | "
            f"{self.neuron_type.value} | "
            f"strength={self.strength:.2f} | "
            f"layer={self.memory_layer.value})"
        )
