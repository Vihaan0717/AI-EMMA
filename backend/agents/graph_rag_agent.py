import networkx as nx
from typing import List, Dict, Optional
import json

class GraphRAGAgent:
    """
    Implements Graph RAG (Retrieval-Augmented Generation).
    Uses an in-memory Knowledge Graph (NetworkX) to store and traverse
    entities and relationships for complex multi-hop reasoning.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self.storage_file = "data/knowledge_graph.json"
        self._load_graph()

    def _load_graph(self):
        try:
            import os
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
        except Exception as e:
            print(f"Failed to load Graph RAG: {e}")

    def _save_graph(self):
        try:
            import os
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            with open(self.storage_file, 'w') as f:
                data = nx.node_link_data(self.graph)
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save Graph RAG: {e}")

    def add_relationship(self, subject: str, relation: str, obj: str, context: str = ""):
        """Adds a triplet to the Knowledge Graph."""
        subject = subject.lower().strip()
        obj = obj.lower().strip()
        
        # Add nodes if they don't exist
        if not self.graph.has_node(subject):
            self.graph.add_node(subject)
        if not self.graph.has_node(obj):
            self.graph.add_node(obj)
            
        # Add edge
        self.graph.add_edge(subject, obj, relation=relation, context=context)
        self._save_graph()

    def query_graph(self, entity: str, max_depth: int = 2) -> List[Dict]:
        """Traverses the graph to find connected context for an entity."""
        entity = entity.lower().strip()
        if not self.graph.has_node(entity):
            return []

        results = []
        # Breadth-first search for multi-hop
        edges = nx.bfs_edges(self.graph, source=entity, depth_limit=max_depth)
        
        # bfs_edges returns generator of (source, target)
        for u, v in edges:
            edge_data = self.graph.get_edge_data(u, v)
            results.append({
                "subject": u,
                "relation": edge_data.get("relation"),
                "object": v,
                "context": edge_data.get("context", "")
            })
            
        return results

graph_rag = GraphRAGAgent()
