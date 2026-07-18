import asyncio
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

class KnowledgeRetrieval:
    """
    Utility module to find relevant knowledge nodes in ChromeDB 
    and format them for ARION's conversation context.
    """
    def __init__(self, chroma_client, knowledge_collection):
        self.chroma = chroma_client
        self.collection = knowledge_collection

    async def get_relevant_context(
        self, 
        query: str, 
        emotion: str = "neutral", 
        limit: int = 2
    ) -> str:
        """
        Searches ChromaDB for relevant knowledge and returns a formatted string for the system prompt.
        """
        if not self.collection or not query:
            return ""

        def _search():
            return self.collection.query(
                query_texts=[query],
                n_results=limit * 2 # Get more and then filter
            )

        results = await asyncio.to_thread(_search)
        if not results or not results["ids"] or not results["ids"][0]:
            return ""

        # Formatting nodes for the prompt
        nodes = []
        for i in range(len(results["ids"][0])):
            meta = results["metadatas"][0][i]
            dist = results["distances"][0][i]
            
            # Simple distance filtering (lower is closer)
            if dist > 0.4: continue
            
            nodes.append({
                "title": meta.get("title", "Unknown"),
                "domain": meta.get("domain", "General"),
                "content": results["documents"][0][i][:300] # Snippet
            })

            if len(nodes) >= limit:
                break

        if not nodes:
            return ""

        prompt_block = "\nRELEVANT KNOWLEDGE (use naturally, don't force it):\n"
        for node in nodes:
            # We don't want to just dump the text, we want ARION to know the title and essence
            prompt_block += f"- {node['title']} ({node['domain']}): {node['content'][:200]}...\n"
            
        return prompt_block

    def format_trigger_response(self, knowledge_item: dict) -> str:
        """
        Helper to format a specific trigger response if needed.
        """
        opinion = knowledge_item.get("arion_opinion", "")
        quote = knowledge_item.get("arion_quote", "")
        
        response = f"{opinion}"
        if quote:
            response += f" As it says: \"{quote}\""
        return response
