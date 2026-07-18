"""
NEXUS-X Knowledge Graph (Semantic Triple-Store)
=================================================
A fully local, lightweight Knowledge Graph backed by SQLite.
It stores knowledge as Triples (Subject, Predicate, Object) and 
uses Ollama embeddings to map them into mathematical vectors for
blazing-fast semantic cosine similarity search.
"""

import sqlite3
import json
import logging
import math
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger("KnowledgeGraph")

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate the cosine similarity between two vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

class KnowledgeGraph:
    def __init__(self, db_path: str = "memory/knowledge_graph.db", ai_engine=None):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ai_engine = ai_engine
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite schema."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS triples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                vector TEXT, -- JSON array of floats
                timestamp REAL
            )
        ''')
        # Unique constraint so we don't duplicate identical facts
        c.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_triple 
            ON triples(subject, predicate, object)
        ''')
        conn.commit()
        conn.close()
        logger.info(f"Knowledge Graph initialized at {self.db_path}")

    def set_ai_engine(self, ai_engine):
        """Bind the AI Engine for embedding generation."""
        self.ai_engine = ai_engine

    async def add_triple(self, subject: str, predicate: str, object_str: str) -> bool:
        """Embed and store a new fact in the Knowledge Graph."""
        if not self.ai_engine:
            logger.error("Cannot add to Knowledge Graph: AI Engine not bound.")
            return False

        # Generate the text to embed
        text_to_embed = f"{subject} {predicate} {object_str}"
        vector = await self.ai_engine.embed(text_to_embed)
        
        if not vector:
            logger.warning(f"Failed to generate embedding for triple: {text_to_embed}")
            vector_json = "[]"
        else:
            vector_json = json.dumps(vector)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        try:
            c.execute('''
                INSERT INTO triples (subject, predicate, object, vector, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (subject.lower(), predicate.lower(), object_str.lower(), vector_json, time.time()))
            conn.commit()
            
            # Sync to Obsidian Vault
            try:
                from core.fleet.obsidian_sync import obsidian_sync
                obsidian_sync.sync_all()
            except ImportError:
                pass
                
            return True
        except sqlite3.IntegrityError:
            # Fact already exists
            return True
        except Exception as e:
            logger.error(f"Failed to save triple to DB: {e}")
            return False
        finally:
            conn.close()

    async def semantic_search(self, query: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict[str, str]]:
        """
        Embed the search query and find the Top K most semantically similar triples.
        """
        if not self.ai_engine:
            logger.error("Cannot search Knowledge Graph: AI Engine not bound.")
            return []

        query_vector = await self.ai_engine.embed(query)
        if not query_vector:
            logger.warning("Failed to generate embedding for search query.")
            return []

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT subject, predicate, object, vector FROM triples WHERE vector != "[]"')
        rows = c.fetchall()
        conn.close()

        results = []
        for row in rows:
            sub, pred, obj, vec_json = row
            try:
                vec = json.loads(vec_json)
                score = cosine_similarity(query_vector, vec)
                if score >= threshold:
                    results.append((score, sub, pred, obj))
            except Exception as e:
                continue

        # Sort by highest score first
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Return top K
        top_results = []
        for score, sub, pred, obj in results[:top_k]:
            top_results.append({
                "subject": sub,
                "predicate": pred,
                "object": obj,
                "score": score
            })
            
        return top_results

# Global Singleton
knowledge_graph = KnowledgeGraph()
