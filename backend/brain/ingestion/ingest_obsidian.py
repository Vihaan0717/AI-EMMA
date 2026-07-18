"""
ObsidianIngestionAgent — The main orchestrator.
Runs the full Synaptic Scan pipeline:

  Vault → NoiseGate → Parser → SynapseFactory → NeuralGraph
                                                     ↓
                                            KnowledgeBase + PatternLearner
                                                     ↓
                                              Reasoning Engine
"""

import asyncio
import logging
import json
import time
from typing    import Dict, List, Optional, Callable
from pathlib   import Path
from datetime  import datetime
from dataclasses import dataclass, field

from .obsidian_parser import ObsidianParser, ParsedNote
from .noise_gate      import NoiseGate, NoiseGateConfig
from .synapse_factory import SynapseFactory
from .neural_graph    import NeuralGraph

# Import reasoning layer
import sys
# Add parent to sys.path to allow relative imports from brain.ingestion to brain.reasoning
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from reasoning.knowledge_base  import KnowledgeBase
from reasoning.pattern_learner import PatternLearner

logger = logging.getLogger("Zero.IngestionAgent")


@dataclass
class IngestionReport:
    """Full report of what was ingested."""
    vault_path:        str
    started_at:        str
    completed_at:      str        = ""
    elapsed_seconds:   float      = 0.0
    total_files:       int        = 0
    passed_gate:       int        = 0
    blocked_gate:      int        = 0
    neurons_created:   int        = 0
    synapses_built:    int        = 0
    kb_entries:        int        = 0
    patterns_learned:  int        = 0
    errors:            List[str]  = field(default_factory=list)
    gate_stats:        Dict       = field(default_factory=dict)
    graph_stats:       Dict       = field(default_factory=dict)
    top_neurons:       List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "vault_path":       self.vault_path,
            "started_at":       self.started_at,
            "completed_at":     self.completed_at,
            "elapsed_seconds":  self.elapsed_seconds,
            "total_files":      self.total_files,
            "passed_gate":      self.passed_gate,
            "blocked_gate":     self.blocked_gate,
            "neurons_created":  self.neurons_created,
            "synapses_built":   self.synapses_built,
            "kb_entries":       self.kb_entries,
            "patterns_learned": self.patterns_learned,
            "errors":           self.errors[:20],  # Cap error list
            "gate_stats":       self.gate_stats,
            "graph_stats":      self.graph_stats,
            "top_neurons":      self.top_neurons,
        }

    def print_summary(self):
        print(f"""
+----------------------------------------------------------+
|         ZERO -- OBSIDIAN INGESTION COMPLETE              |
+----------------------------------------------------------+
|  Vault          : {self.vault_path[:40]:<40} |
|  Duration       : {self.elapsed_seconds:.1f}s{'':<42} |
+----------------------------------------------------------+
|  Files scanned     : {self.total_files:<34} |
|  Passed NoiseGate  : {self.passed_gate:<34} |
|  Blocked by Gate   : {self.blocked_gate:<34} |
+----------------------------------------------------------+
|  Neurons created   : {self.neurons_created:<34} |
|  Synapses built    : {self.synapses_built:<34} |
|  KB entries stored : {self.kb_entries:<34} |
|  Patterns learned  : {self.patterns_learned:<34} |
+----------------------------------------------------------+
|  Top neurons (most connected):                           |""")
        for i, n in enumerate(self.top_neurons[:5], 1):
            label = n.get("label", "?")[:30]
            act   = n.get("activation", 0)
            print(f"|     {i}. {label:<30} [{act:.2f}] |")
        print("+----------------------------------------------------------+")


class ObsidianIngestionAgent:
    """
    Orchestrates the entire ingestion process.
    Syncs Obsidian vault to Zero Neural Core.
    """

    def __init__(self, vault_path: str | Path):
        self.vault_path = Path(vault_path)
        self.parser     = ObsidianParser(self.vault_path)
        self.gate       = NoiseGate()
        self.graph      = NeuralGraph()
        self.factory    = SynapseFactory(self.graph)
        
        # Supporting reasoning components
        self.kb         = KnowledgeBase()
        self.learner    = PatternLearner()

    async def run_ingestion(self, full_sync: bool = False) -> IngestionReport:
        """Run the full ingestion pipeline."""
        start_time = time.time()
        report = IngestionReport(
            vault_path=str(self.vault_path),
            started_at=datetime.utcnow().isoformat()
        )

        if full_sync:
            self.gate.upgrade_to_full_sync()

        logger.info(f"🚀 Starting ingestion pipeline: {self.vault_path}")

        # ── Step 1: Scan & Parse with NoiseGate ───────────────────
        passed_notes: List[ParsedNote] = []
        
        for note in self.parser.scan_vault():
            report.total_files += 1
            
            passes, score, reason = self.gate.evaluate(note.to_dict(), self.vault_path)
            
            if passes:
                passed_notes.append(note)
                report.passed_gate += 1
            else:
                report.blocked_gate += 1

        # ── Step 2: Batch build neurons and synapses ─────────────
        if passed_notes:
            graph_results = self.factory.batch_build_all(passed_notes)
            report.neurons_created = graph_results.get("neurons_created", 0)
            report.synapses_built  = graph_results.get("total_synapses", 0)
            report.graph_stats     = graph_results.get("graph_stats", {})
            report.top_neurons     = report.graph_stats.get("top_nodes", [])

            # ── Step 3: Store in KnowledgeBase & PatternLearner ──────
            for note in passed_notes:
                try:
                    # Store in KB
                    self.kb.store(
                        topic=note.title,
                        content=note.body,
                        tags=note.tags,
                        source="obsidian",
                        summary=note.frontmatter.get("description", "")
                    )
                    report.kb_entries += 1

                    # Learn as a pattern if it has a summary/explanation
                    if note.word_count > 100:
                        self.learner.store_pattern(
                            query=f"What is {note.title}?",
                            response={
                                "answer": note.body[:2000],
                                "confidence": 0.9,
                                "analysis": {"source": "obsidian_sync"}
                            },
                            tags=note.tags,
                            source="obsidian"
                        )
                        report.patterns_learned += 1
                except Exception as e:
                    report.errors.append(f"KB/Pattern error in {note.title}: {e}")

        # ── Finalize Report ───────────────────────────────────────
        report.completed_at    = datetime.utcnow().isoformat()
        report.elapsed_seconds = round(time.time() - start_time, 2)
        report.gate_stats      = self.gate.stats()

        logger.info(f"DONE: Ingestion complete in {report.elapsed_seconds}s")
        return report

    async def sync_file(self, filepath: Path) -> bool:
        """
        Incremental sync: Ingest a single file into the neural core.
        Called by ObsidianWatcher on file changes.
        """
        try:
            note = self.parser.parse_file(filepath)
            if not note:
                return False
                
            # Gate check
            passes, score, reason = self.gate.evaluate(note.to_dict(), self.vault_path)
            if not passes:
                logger.debug(f"Gate blocked sync for {filepath.name}: {reason}")
                return False
                
            # Register neuron
            nid = self.factory.register_note(note)
            
            # Build connections to existing neurons
            # We fetch a large sample of known labels to resolve links
            all_neurons = {n['label'].lower(): n['id'] for n in self.graph.get_strongest_neurons(2000)}
            self.factory.build_connections(note, all_neurons)
            
            # Store in KB
            self.kb.store(
                topic=note.title,
                content=note.body,
                tags=note.tags,
                source="obsidian_watcher",
                summary=note.frontmatter.get("description", "")
            )
            
            # Learn pattern if substantial
            if note.word_count > 50:
                self.learner.store_pattern(
                    query=f"What is {note.title}?",
                    response={
                        "answer": note.body[:2000],
                        "confidence": 0.85,
                        "analysis": {"source": "obsidian_watcher"}
                    },
                    tags=note.tags,
                    source="obsidian_watcher"
                )
            
            logger.info(f"Synced neural node: {note.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to sync file {filepath.name}: {e}")
            return False


async def main():
    """CLI Entry point for standalone ingestion."""
    # Default vault path for JARVIS
    vault = Path(r"c:\Users\anger\Desktop\JARVIS_Project\JARVIS-v2\arion\vault")
    if not vault.exists():
        # Try local project obsidian folder if vault doesn't exist
        vault = Path(r"c:\Users\anger\Desktop\JARVIS_Project\knowledge_vault")
    
    agent = ObsidianIngestionAgent(vault)
    report = await agent.run_ingestion(full_sync=True)
    report.print_summary()


if __name__ == "__main__":
    import sys
    # Set logging level
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    asyncio.run(main())
