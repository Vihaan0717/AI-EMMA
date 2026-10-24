import sqlite3
import os
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Entity(BaseModel):
    entity_id: str = Field(default_factory=generate_uuid)
    name: str
    type: str # e.g. PERSON, CONCEPT, TECHNOLOGY

class Relationship(BaseModel):
    rel_id: str = Field(default_factory=generate_uuid)
    source_entity_id: str
    target_entity_id: str
    relation_type: str # e.g. related_to, causes, contradicts, supported_by
    evidence_id: Optional[str] = None # Link to MemoryItem

class KnowledgeGraph:
    def __init__(self, db_path: str = "logs/knowledge_graph.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                rel_id TEXT PRIMARY KEY,
                source_entity_id TEXT,
                target_entity_id TEXT,
                relation_type TEXT,
                evidence_id TEXT,
                FOREIGN KEY(source_entity_id) REFERENCES entities(entity_id),
                FOREIGN KEY(target_entity_id) REFERENCES entities(entity_id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_entity(self, entity: Entity):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO entities (entity_id, name, type) VALUES (?, ?, ?)',
                  (entity.entity_id, entity.name, entity.type))
        conn.commit()
        conn.close()

    def add_relationship(self, rel: Relationship):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO relationships 
            (rel_id, source_entity_id, target_entity_id, relation_type, evidence_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', (rel.rel_id, rel.source_entity_id, rel.target_entity_id, rel.relation_type, rel.evidence_id))
        conn.commit()
        conn.close()

    def get_related_entities(self, entity_name: str) -> List[Dict[str, str]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT e2.name, r.relation_type, e2.type 
            FROM entities e1
            JOIN relationships r ON e1.entity_id = r.source_entity_id
            JOIN entities e2 ON r.target_entity_id = e2.entity_id
            WHERE e1.name = ?
        ''', (entity_name,))
        rows = c.fetchall()
        conn.close()
        return [{"target": r[0], "relation": r[1], "target_type": r[2]} for r in rows]
