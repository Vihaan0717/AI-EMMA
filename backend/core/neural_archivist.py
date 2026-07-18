import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger("NeuralArchivist")

class NeuralArchivist:
    """
    The memory-growth engine for JARVIS-X.
    Analyzes historical logs and chat data to improve persona and word accuracy.
    """
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.db_path = self.root / "memory" / "fleet.db"
        self.rules_path = self.root / "config" / "linguistic_rules.json"
        self.persona_growth_path = self.root / "memory" / "persona_learnings.json"
        
        # Default rules to prevent common errors (like the Anni confusion)
        self.default_rules = {
            "vocabulary": {
                "anni": {"meaning": "all/everything", "category": "quantifier", "language": "telugu"},
                "ra": {"meaning": "casual suffix", "category": "marker", "language": "telugu"},
                "garu": {"meaning": "respectful suffix", "category": "marker", "language": "telugu"}
            },
            "name_exceptions": ["anni", "ra", "garu", "meeru", "aap"],
            "code_switching_patterns": []
        }
        self._ensure_paths()

    def _ensure_paths(self):
        if not self.rules_path.exists():
            with open(self.rules_path, "w", encoding="utf-8") as f:
                json.dump(self.default_rules, f, indent=4)
        if not self.persona_growth_path.exists():
            with open(self.persona_growth_path, "w", encoding="utf-8") as f:
                json.dump({"learnings": [], "last_sync": ""}, f, indent=4)

    def run_learning_cycle(self):
        """Perform a full analysis of recent interactions and external data."""
        logger.info("Starting Neural Learning Cycle...")
        try:
            # 1. Internal Logs
            logs = self._get_recent_logs()
            
            # 2. External Ingestion
            external_data = self._ingest_external_data()
            all_data = logs + external_data

            if not all_data:
                logger.info("No data to analyze.")
                return

            analysis = self._analyze_patterns(all_data)
            self._update_growth_file(analysis)
            logger.info(f"Learning cycle complete. {len(all_data)} interactions analyzed.")
            return analysis
        except Exception as e:
            logger.error(f"Learning cycle failed: {e}")

    def _ingest_external_data(self) -> List[Dict]:
        """Read and parse chat exports from brain/ingestion/"""
        ingestion_dir = self.root / "brain" / "ingestion"
        external_logs = []
        
        for file in ingestion_dir.glob("*.*"):
            if file.suffix in [".txt", ".json"]:
                logger.info(f"Ingesting {file.name}...")
                try:
                    if file.suffix == ".json":
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            # Basic mapping for generic JSON exports
                            if isinstance(data, list):
                                for item in data:
                                    external_logs.append({
                                        "task": item.get("text", item.get("message", "")),
                                        "sender": item.get("from", "owner"),
                                        "timestamp": item.get("date", "")
                                    })
                    else:
                        with open(file, "r", encoding="utf-8") as f:
                            for line in f:
                                # Simple line-based text parsing
                                if ":" in line:
                                    parts = line.split(":", 1)
                                    external_logs.append({
                                        "task": parts[1].strip(),
                                        "sender": "owner",
                                        "timestamp": ""
                                    })
                except Exception as e:
                    logger.error(f"Failed to ingest {file.name}: {e}")
        return external_logs

    def _get_recent_logs(self) -> List[Dict]:
        """Fetch logs from the fleet database."""
        if not self.db_path.exists(): return []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get logs from the last 24 hours
        cursor.execute("""
            SELECT agent_id, task, score, critic_feedback, timestamp 
            FROM interaction_logs 
            ORDER BY timestamp DESC LIMIT 100
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def _analyze_patterns(self, logs: List[Dict]) -> Dict:
        """Extract linguistic and behavioral patterns."""
        patterns = {
            "top_words": {},
            "mixed_language_ratio": 0.0,
            "detected_names": set(),
            "sentiment_trend": 0.0,
            "linguistic_corrections": []
        }
        
        total_telugu_words = 0
        total_english_words = 0
        
        for log in logs:
            text = log["task"].lower()
            words = text.split()
            
            # Simple language heuristic
            telugu_markers = ["ga", "unnaru", "unnava", "enti", "em", "anni", "chesi"]
            for word in words:
                if word in telugu_markers:
                    total_telugu_words += 1
                else:
                    total_english_words += 1
            
            # Detect potential name confusion
            if "anni" in words:
                patterns["linguistic_corrections"].append({
                    "word": "anni",
                    "context": text,
                    "resolution": "Confirmed quantifier 'all', not a name."
                })

        if (total_telugu_words + total_english_words) > 0:
            patterns["mixed_language_ratio"] = total_telugu_words / (total_telugu_words + total_english_words)
            
        patterns["detected_names"] = list(patterns["detected_names"]) # JSON serializable
        return patterns

    def _update_growth_file(self, analysis: Dict):
        """Persist findings to the growth file."""
        with open(self.persona_growth_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        data["learnings"].append({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis
        })
        data["last_sync"] = datetime.now().isoformat()
        
        with open(self.persona_growth_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    archivist = NeuralArchivist()
    res = archivist.run_learning_cycle()
    print(json.dumps(res, indent=4))
