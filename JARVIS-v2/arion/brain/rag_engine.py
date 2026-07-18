
"""
RAGEngine (Hippocampus) — ARION's Semantic Retrieval System.
Manages multiple ChromaDB collections mapped to human brain regions.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

class RAGEngine:

    def __init__(self, chroma_path: str = "arion/data/chromadb"):
        import chromadb
        self.client = chromadb.PersistentClient(path=chroma_path)
        
        # Human Brain Mapped Collections
        self.collections = {
            "episodic":   self.client.get_or_create_collection("episodic_memories"), # Specific events
            "semantic":   self.client.get_or_create_collection("semantic_facts"),   # People facts
            "knowledge":  self.client.get_or_create_collection("knowledge_base"),   # Books/Movies/Philosophy
            "procedural": self.client.get_or_create_collection("procedural_slang"), # Slang/Behaviors
            "working":    self.client.get_or_create_collection("working_context"),  # Current session buffer
        }
        print(f"[RAGEngine] Hippocampus online. 5 neural collections active.", flush=True)

    async def query(self, text: str, domains: List[str] = None, n_results: int = 3) -> Dict[str, List[Dict]]:
        """Queries multiple collections and returns a consolidated context."""
        if not domains:
            domains = list(self.collections.keys())
        
        results = {}
        import asyncio
        for domain in domains:
            if domain not in self.collections: continue
            
            try:
                # Offload blocking ChromaDB query to thread
                res = await asyncio.to_thread(
                    self.collections[domain].query,
                    query_texts=[text],
                    n_results=n_results
                )
                
                domain_results = []
                if res["documents"] and res["documents"][0]:
                    for i in range(len(res["documents"][0])):
                        domain_results.append({
                            "content": res["documents"][0][i],
                            "metadata": res["metadatas"][0][i] if res["metadatas"] else {},
                            "distance": res["distances"][0][i] if res["distances"] else 0
                        })
                results[domain] = domain_results
            except Exception as e:
                print(f"[RAGEngine] Error querying {domain}: {e}")
                results[domain] = []
                
        return results

    def add_memory(self, domain: str, content: str, metadata: Dict[str, Any]):
        """Adds a new memory to a specific neural collection."""
        if domain not in self.collections:
            print(f"[RAGEngine] Invalid domain: {domain}")
            return
            
        try:
            self.collections[domain].add(
                documents=[content],
                metadatas=[metadata],
                ids=[str(uuid.uuid4())]
            )
        except Exception as e:
            print(f"[RAGEngine] Error adding to {domain}: {e}")

    def get_context_string(self, query_results: Dict[str, List[Dict]]) -> str:
        """Converts raw results into a clean system prompt injection."""
        lines = []
        
        # 1. Facts (Semantic)
        facts = query_results.get("semantic", [])
        if facts:
            lines.append("\nPEOPLE & FACTS:")
            for f in facts:
                if f["distance"] < 0.4: # Only high-confidence
                    lines.append(f"- {f['content']}")

        # 2. Past Events (Episodic)
        episodes = query_results.get("episodic", [])
        if episodes:
            lines.append("\nRELEVANT PAST MOMENTS:")
            for e in episodes:
                if e["distance"] < 0.4:
                    lines.append(f"- {e['content']}")
                    
        # 3. Knowledge
        knowledge = query_results.get("knowledge", [])
        if knowledge:
            lines.append("\nEXTERNAL KNOWLEDGE:")
            for k in knowledge:
                if k["distance"] < 0.5:
                    lines.append(f"- {k['content']}")

        return "\n".join(lines) if lines else ""

    async def retrieve(self, query: str, memory_types: List[str], n_results: int = 5, min_relevance: float = 0.45) -> List[Dict]:
        """
        Specific retrieval for memory questions. 
        Returns a flat list of results from specified collections.
        """
        all_res = await self.query(query, domains=memory_types, n_results=n_results)
        flat = []
        for domain, items in all_res.items():
            for item in items:
                # distance < (1 - min_relevance) assuming relevance is 0..1
                # or just use the user's suggested thresholding
                if item["distance"] <= (1.0 - min_relevance):
                    item["domain"] = domain
                    flat.append(item)
        
        # Sort by distance (relevance)
        flat.sort(key=lambda x: x["distance"])
        return flat[:n_results]

    def format_memories_for_prompt(self, memories: List[Dict], max_chars: int = 400) -> str:
        """Compact formatting for prompt injection."""
        if not memories: return ""
        
        lines = ["EXPLICIT MEMORY RECALL (High Relevance):"]
        current_len = 0
        for m in memories:
            entry = f"- [{m['domain'].upper()}] {m['content']}"
            if current_len + len(entry) > max_chars:
                break
            lines.append(entry)
            current_len += len(entry)
            
        return "\n".join(lines)
