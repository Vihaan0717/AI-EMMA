"""
Obsidian Sync Service
=====================
Exports the SQLite Knowledge Graph triples to Obsidian Markdown files.
Each unique subject gets its own file with Dataview-compatible links
to objects, building a visual graph in Obsidian.
"""

import sqlite3
import os
import logging
from pathlib import Path

logger = logging.getLogger("ObsidianSync")

class ObsidianSync:
    def __init__(self, db_path: str = "memory/knowledge_graph.db", vault_path: str = r"C:\Users\anger\Desktop\JARVIS-v2\arion\vault"):
        self.db_path = db_path
        self.vault_path = Path(vault_path)
        
    def sync_all(self):
        """Export all triples from the DB to the Obsidian vault."""
        if not os.path.exists(self.db_path):
            logger.warning("Knowledge Graph DB not found. Nothing to sync.")
            return

        try:
            self.vault_path.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Group by subject
            c.execute('SELECT subject, predicate, object FROM triples')
            rows = c.fetchall()
            conn.close()
            
            if not rows:
                return
                
            nodes = {}
            for sub, pred, obj in rows:
                # Sanitize filenames
                clean_sub = "".join([c for c in sub if c.isalnum() or c in " _-"]).strip()
                if not clean_sub:
                    continue
                    
                if clean_sub not in nodes:
                    nodes[clean_sub] = []
                    
                nodes[clean_sub].append((pred, obj))
                
            # Write markdown files
            for subject, relationships in nodes.items():
                file_path = self.vault_path / f"{subject}.md"
                
                content = f"---\ntags:\n  - jarvis/memory_node\n---\n\n# {subject.title()}\n\n"
                content += "## Relationships\n"
                
                for pred, obj in relationships:
                    # Sanitize object for linking
                    clean_obj = "".join([c for c in obj if c.isalnum() or c in " _-"]).strip()
                    content += f"- **{pred}** :: [[{clean_obj}]]\n"
                    
                # Write file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                    
            logger.info(f"Obsidian Sync complete: Exported {len(nodes)} nodes to {self.vault_path}")
            
        except Exception as e:
            logger.error(f"Obsidian sync failed: {e}")

# Global singleton
obsidian_sync = ObsidianSync()
