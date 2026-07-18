"""
NeuralGraph — The living knowledge graph.
Nodes  = Concepts / Notes
Edges  = [[backlinks]] between them
Weights = Synaptic strength (Hebbian: fire together → wire together)

Storage: SQLite (no Neo4j dependency — lightweight, self-contained)
"""

import sqlite3
import json
import logging
import math
from typing      import Dict, List, Optional, Tuple, Set
from pathlib     import Path
from datetime    import datetime
from dataclasses import dataclass, field

logger = logging.getLogger("Zero.NeuralGraph")

DB_PATH = Path(__file__).parent.parent / "data" / "neural_graph.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class Neuron:
    """A node in the knowledge graph — represents one concept/note."""
    id:              int
    label:           str           # Note title
    note_path:       str
    tags:            List[str]     = field(default_factory=list)
    activation:      float         = 0.5   # 0.0 - 1.0
    decay_rate:      float         = 0.02  # Per day if not accessed
    access_count:    int           = 0
    created_at:      str           = ""
    last_activated:  str           = ""


@dataclass
class Synapse:
    """A directed edge — represents [[link]] from source to target."""
    source_id:   int
    target_id:   int
    strength:    float = 0.5   # Hebbian weight: 0.0 - 1.0
    co_activations: int = 1    # How many times both fired together
    created_at:  str   = ""
    last_fired:  str   = ""


class NeuralGraph:
    """
    Knowledge graph with Hebbian learning.
    
    Hebbian Rule:  "Neurons that fire together, wire together."
    In practice:   When note A is queried alongside note B,
                   the A→B synapse strength increases.
    
    Decay Rule:    Unused synapses weaken over time.
                   strength -= decay_rate * days_inactive
    """

    # ── Hebbian parameters ────────────────────────────────────────
    HEBBIAN_BOOST    = 0.05   # Strength increase per co-activation
    DECAY_RATE       = 0.02   # Strength loss per day of inactivity
    MAX_STRENGTH     = 1.00
    MIN_STRENGTH     = 0.01   # Below this → synapse pruned

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory  = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")   # Better concurrent access
        self._init_db()
        logger.info(f"✅ NeuralGraph ready | {self.neuron_count()} neurons, "
                    f"{self.synapse_count()} synapses")

    # ═══════════════════════════════════════════════════════════════
    #  DB SETUP
    # ═══════════════════════════════════════════════════════════════

    def _init_db(self):
        c = self.conn.cursor()

        # Neurons (nodes)
        c.execute("""
            CREATE TABLE IF NOT EXISTS neurons (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                label           TEXT    NOT NULL,
                note_path       TEXT    UNIQUE NOT NULL,
                tags            TEXT    DEFAULT '[]',
                activation      REAL    DEFAULT 0.5,
                decay_rate      REAL    DEFAULT 0.02,
                access_count    INTEGER DEFAULT 0,
                summary         TEXT    DEFAULT '',
                word_count      INTEGER DEFAULT 0,
                created_at      TEXT    NOT NULL,
                last_activated  TEXT    NOT NULL
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_neurons_label ON neurons(label)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_neurons_tags  ON neurons(tags)")

        # Synapses (edges) — directed graph
        c.execute("""
            CREATE TABLE IF NOT EXISTS synapses (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id       INTEGER NOT NULL REFERENCES neurons(id),
                target_id       INTEGER NOT NULL REFERENCES neurons(id),
                strength        REAL    DEFAULT 0.5,
                co_activations  INTEGER DEFAULT 1,
                created_at      TEXT    NOT NULL,
                last_fired      TEXT    NOT NULL,
                UNIQUE(source_id, target_id)
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_syn_source ON synapses(source_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_syn_target ON synapses(target_id)")

        # Activation log (for pattern analysis)
        c.execute("""
            CREATE TABLE IF NOT EXISTS activation_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                neuron_id   INTEGER NOT NULL REFERENCES neurons(id),
                trigger     TEXT    DEFAULT '',
                activated_at TEXT   NOT NULL
            )
        """)

        self.conn.commit()

    # ═══════════════════════════════════════════════════════════════
    #  NEURON OPERATIONS
    # ═══════════════════════════════════════════════════════════════

    def upsert_neuron(self, note_path: str, label: str, **kwargs) -> int:
        """
        Insert or update a neuron.
        Returns neuron ID.
        """
        now = datetime.utcnow().isoformat()
        c   = self.conn.cursor()

        existing = c.execute(
            "SELECT id FROM neurons WHERE note_path = ?", (note_path,)
        ).fetchone()

        if existing:
            # Update existing neuron
            c.execute("""
                UPDATE neurons SET
                    label          = ?,
                    tags           = ?,
                    summary        = ?,
                    word_count     = ?,
                    last_activated = ?
                WHERE note_path = ?
            """, (
                label,
                json.dumps(kwargs.get("tags", [])),
                kwargs.get("summary", "")[:500],
                kwargs.get("word_count", 0),
                now,
                note_path
            ))
            self.conn.commit()
            return existing["id"]
        else:
            # Create new neuron
            c.execute("""
                INSERT INTO neurons
                    (label, note_path, tags, activation, decay_rate,
                     summary, word_count, created_at, last_activated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                label,
                note_path,
                json.dumps(kwargs.get("tags", [])),
                kwargs.get("initial_activation", 0.5),
                self.DECAY_RATE,
                kwargs.get("summary", "")[:500],
                kwargs.get("word_count", 0),
                now, now
            ))
            self.conn.commit()
            return c.lastrowid

    def activate_neuron(self, neuron_id: int, trigger: str = "") -> float:
        """
        Fire a neuron — increases activation, logs it.
        Returns new activation level.
        """
        now = datetime.utcnow().isoformat()
        c   = self.conn.cursor()

        row = c.execute(
            "SELECT activation, access_count FROM neurons WHERE id = ?",
            (neuron_id,)
        ).fetchone()

        if not row:
            return 0.0

        # Activation increases toward 1.0 with each access
        new_activation = min(
            self.MAX_STRENGTH,
            row["activation"] + 0.05
        )

        c.execute("""
            UPDATE neurons SET
                activation     = ?,
                access_count   = access_count + 1,
                last_activated = ?
            WHERE id = ?
        """, (new_activation, now, neuron_id))

        # Log activation
        c.execute(
            "INSERT INTO activation_log (neuron_id, trigger, activated_at) VALUES (?, ?, ?)",
            (neuron_id, trigger[:100], now)
        )

        self.conn.commit()
        return new_activation

    # ═══════════════════════════════════════════════════════════════
    #  SYNAPSE OPERATIONS
    # ═══════════════════════════════════════════════════════════════

    def create_synapse(
        self,
        source_id: int,
        target_id: int,
        initial_strength: float = 0.5
    ) -> bool:
        """
        Create or strengthen a synapse.
        If it exists, boost its strength (Hebbian).
        """
        if source_id == target_id:
            return False

        now = datetime.utcnow().isoformat()
        c   = self.conn.cursor()

        existing = c.execute(
            "SELECT id, strength, co_activations FROM synapses "
            "WHERE source_id = ? AND target_id = ?",
            (source_id, target_id)
        ).fetchone()

        if existing:
            new_strength = min(
                self.MAX_STRENGTH,
                existing["strength"] + self.HEBBIAN_BOOST
            )
            c.execute("""
                UPDATE synapses SET
                    strength       = ?,
                    co_activations = co_activations + 1,
                    last_fired     = ?
                WHERE id = ?
            """, (new_strength, now, existing["id"]))
        else:
            c.execute("""
                INSERT OR IGNORE INTO synapses
                    (source_id, target_id, strength, co_activations,
                     created_at, last_fired)
                VALUES (?, ?, ?, 1, ?, ?)
            """, (source_id, target_id, initial_strength, now, now))

        self.conn.commit()
        return True

    def hebbian_update(self, activated_neuron_ids: List[int]):
        """
        Batch Hebbian update after a query session.
        All neurons in the activated set fire together
        → strengthen all pairwise synapses between them.
        """
        if len(activated_neuron_ids) < 2:
            return

        pairs_updated = 0
        for i, source in enumerate(activated_neuron_ids):
            for target in activated_neuron_ids[i+1:]:
                self.create_synapse(source, target)
                pairs_updated += 1

        logger.debug(
            f"🔥 Hebbian update: {len(activated_neuron_ids)} neurons, "
            f"{pairs_updated} synapses reinforced"
        )

    # ═══════════════════════════════════════════════════════════════
    #  DECAY
    # ═══════════════════════════════════════════════════════════════

    def apply_decay(self) -> Dict:
        """
        Apply synaptic decay to all inactive synapses.
        Run this on a schedule (e.g., daily).
        Prunes synapses that fall below MIN_STRENGTH.
        """
        now  = datetime.utcnow()
        c    = self.conn.cursor()
        rows = c.execute(
            "SELECT id, strength, last_fired FROM synapses"
        ).fetchall()

        decayed = 0
        pruned  = 0

        for row in rows:
            try:
                last = datetime.fromisoformat(row["last_fired"])
                days_inactive = (now - last).days

                if days_inactive < 1:
                    continue

                new_strength = row["strength"] - (self.DECAY_RATE * days_inactive)

                if new_strength < self.MIN_STRENGTH:
                    c.execute("DELETE FROM synapses WHERE id = ?", (row["id"],))
                    pruned += 1
                else:
                    c.execute(
                        "UPDATE synapses SET strength = ? WHERE id = ?",
                        (round(new_strength, 4), row["id"])
                    )
                    decayed += 1
            except Exception:
                continue

        self.conn.commit()
        result = {"decayed": decayed, "pruned": pruned, "total": len(rows)}
        logger.info(f"🌿 Decay applied: {decayed} weakened, {pruned} pruned")
        return result

    # ═══════════════════════════════════════════════════════════════
    #  GRAPH TRAVERSAL
    # ═══════════════════════════════════════════════════════════════

    def find_related(
        self,
        neuron_id: int,
        depth: int = 2,
        min_strength: float = 0.3
    ) -> List[Dict]:
        """
        BFS traversal: find all neurons connected within `depth` hops.
        Returns sorted by combined path strength (strongest first).
        """
        visited: Set[int]   = {neuron_id}
        frontier: List[int] = [neuron_id]
        results:  List[Dict] = []

        for hop in range(depth):
            next_frontier = []
            for nid in frontier:
                rows = self.conn.execute("""
                    SELECT s.target_id, s.strength, n.label, n.summary, n.activation
                    FROM synapses s
                    JOIN neurons n ON s.target_id = n.id
                    WHERE s.source_id = ? AND s.strength >= ?
                    ORDER BY s.strength DESC
                    LIMIT 15
                """, (nid, min_strength)).fetchall()

                for row in rows:
                    tid = row["target_id"]
                    if tid not in visited:
                        visited.add(tid)
                        next_frontier.append(tid)
                        results.append({
                            "neuron_id":  tid,
                            "label":      row["label"],
                            "summary":    row["summary"],
                            "strength":   row["strength"],
                            "activation": row["activation"],
                            "hop":        hop + 1
                        })
            frontier = next_frontier

        # Sort: high strength + high activation first
        results.sort(
            key=lambda r: (r["strength"] * 0.7 + r["activation"] * 0.3),
            reverse=True
        )
        return results

    def get_neuron_by_label(self, label: str) -> Optional[Dict]:
        """Find a neuron by its label (note title)."""
        row = self.conn.execute(
            "SELECT * FROM neurons WHERE label = ? COLLATE NOCASE",
            (label,)
        ).fetchone()
        return dict(row) if row else None

    def get_strongest_neurons(self, limit: int = 20) -> List[Dict]:
        """Return neurons with highest activation — the 'core knowledge'."""
        rows = self.conn.execute("""
            SELECT n.*, COUNT(s.id) AS synapse_count
            FROM neurons n
            LEFT JOIN synapses s ON n.id = s.source_id
            GROUP BY n.id
            ORDER BY n.activation DESC, synapse_count DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def graph_stats(self) -> Dict:
        return {
            "neurons":   self.neuron_count(),
            "synapses":  self.synapse_count(),
            "avg_strength": self._avg_strength(),
            "top_nodes": [
                {"label": r["label"], "activation": r["activation"]}
                for r in self.get_strongest_neurons(5)
            ]
        }

    def neuron_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM neurons").fetchone()[0]

    def synapse_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM synapses").fetchone()[0]

    def _avg_strength(self) -> float:
        row = self.conn.execute("SELECT AVG(strength) FROM synapses").fetchone()
        return round(row[0] or 0.0, 4)
