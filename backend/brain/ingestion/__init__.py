"""
Obsidian → Zero Neural Core: Ingestion Protocol
Synaptic Scan approach — Nodes, Edges, Weights, Decay
"""

from .ingest_obsidian   import ObsidianIngestionAgent
from .obsidian_parser   import ObsidianParser
from .synapse_factory   import SynapseFactory
from .noise_gate        import NoiseGate
from .neural_graph      import NeuralGraph

__all__ = [
    "ObsidianIngestionAgent",
    "ObsidianParser",
    "SynapseFactory",
    "NoiseGate",
    "NeuralGraph"
]

PROTOCOL_VERSION = "1.0.0"
PHASE            = "filtered_sync"   # Upgrade to "full_sync" in Phase 2
