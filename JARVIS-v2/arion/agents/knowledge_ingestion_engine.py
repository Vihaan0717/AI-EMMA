import asyncio
import json
import os
import re
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

import chromadb
import aiohttp

from core.base_agent import BaseAgent
from core.message_bus import Channel, Message, Priority

class KnowledgeIngestionEngine(BaseAgent):
    def __init__(self, config: dict):
        super().__init__("KnowledgeIngestionEngine", [Channel.KNOWLEDGE])
        self.vault_path = Path(config.get("db_paths", {}).get("obsidian_vault", "arion/vault"))
        self.chroma_path = config.get("db_paths", {}).get("chroma", "arion/data/chromadb")
        self.ollama_url = config.get("ollama_url", "http://localhost:11434")
        self.model = config.get("model_name", "llama3.1")
        
        self.chroma_client = None
        self.knowledge_collection = None

    async def _init_chroma(self):
        def _setup():
            client = chromadb.PersistentClient(path=self.chroma_path)
            # Separate collection for knowledge to keep it clean from personal/slang memories
            collection = client.get_or_create_collection(name="arion_knowledge")
            return client, collection
        
        self.chroma_client, self.knowledge_collection = await asyncio.to_thread(_setup)
        print("[KnowledgeIngestionEngine] ChromaDB Knowledge Collection Ready.", flush=True)

    async def run_loop(self):
        await self._init_chroma()
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "ingest_content":
            payload = message.payload
            result = await self.ingest(
                content=payload.get("content", ""),
                domain=payload.get("domain", "general"),
                title=payload.get("title", "Unknown"),
                source_type=payload.get("source_type", "manual")
            )
            if message.requires_response:
                await self.respond_to(message, "content_ingested", {"result": "success", "node_id": result.get("id")})
        
        elif message.action == "search_knowledge":
            query = message.payload.get("query", "")
            results = await self._search_existing_knowledge(query, limit=message.payload.get("limit", 5))
            if message.requires_response:
                await self.respond_to(message, "knowledge_results", {"results": results})

    async def ingest(self, content: str, domain: str, title: str, source_type: str = "text") -> dict:
        print(f"[KnowledgeIngestionEngine] Ingesting: '{title}' ({domain})", flush=True)
        
        # Step 1: Extract facts
        raw_facts = await self._extract_facts(content, domain, title)
        
        # Step 2: Form perspective
        arion_view = await self._form_perspective(content, raw_facts, domain, title)
        
        # Step 3: Identify connections (Mocked for now, will hit ChromaDB)
        connections = await self._find_connections(raw_facts, domain)
        
        # Step 4: Identify triggers
        context_triggers = await self._identify_triggers(raw_facts, arion_view, domain)
        
        # Step 5: Build node
        node = {
            "id": f"{domain}_{title.lower().replace(' ', '_')}_{int(time.time())}",
            "title": title,
            "domain": domain,
            "ingested": datetime.now().isoformat(),
            "essence": raw_facts.get("essence", ""),
            "themes": raw_facts.get("themes", []),
            "key_facts": raw_facts.get("key_facts", []),
            "arion_opinion": arion_view.get("opinion", ""),
            "arion_rating": arion_view.get("rating", 5),
            "arion_quote": arion_view.get("memorable_quote", ""),
            "emotional_weight": arion_view.get("emotional_weight", "neutral"),
            "connects_to": connections,
            "context_triggers": context_triggers,
            "times_referenced": 0
        }
        
        # Step 6: Save to vault
        await self._save_to_vault(node)
        
        # Step 7: Index in Chroma
        await self._index_in_chroma(node)
        
        print(f"[KnowledgeIngestionEngine] OK: Ingested '{title}'", flush=True)
        return node

    async def _extract_facts(self, content: str, domain: str, title: str) -> dict:
        instruction = f"Extract core essence, 5 themes, and 5 key facts for this {domain} piece."
        # Domain specific nuances...
        
        messages = [
            {"role": "system", "content": f"You are a knowledge extraction engine specialized in South Asian contexts. {instruction} Handle Romanized Telugu scripts by translating key facts to English while preserving specific cultural nouns. Return ONLY valid JSON. Format: {{\"essence\": \"...\", \"themes\": [], \"key_facts\": []}}"},
            {"role": "user", "content": f"Title: {title}\nContent: {content[:4000]}"}
        ]
        
        res = await self._ollama_request(messages)
        return self._parse_json(res, {"essence": content[:200], "themes": [], "key_facts": []})

    async def _form_perspective(self, content: str, facts: dict, domain: str, title: str) -> dict:
        messages = [
            {"role": "system", "content": "You are ARION, a sharp, sarcastic, caring digital intelligence. Form your genuine opinion on this topic. Format: {{\"opinion\": \"...\", \"rating\": 8, \"memorable_quote\": \"...\", \"emotional_weight\": \"...\"}}"},
            {"role": "user", "content": f"Topic: {title}. Essence: {facts['essence']}"}
        ]
        res = await self._ollama_request(messages)
        return self._parse_json(res, {"opinion": "Interesting stuff ra.", "rating": 5, "memorable_quote": "", "emotional_weight": "neutral"})

    async def _find_connections(self, facts: dict, domain: str) -> list:
        # Search ChromaDB for related existing knowledge
        themes = facts.get("themes", [])
        if not themes: return []
        
        results = await self._search_existing_knowledge(" ".join(themes[:3]), limit=3)
        connections = []
        for r in results:
            if r["id"] != facts.get("id"): # Don't connect to itself
                connections.append({"id": r["id"], "title": r["title"], "domain": r["domain"]})
        return connections

    async def _identify_triggers(self, facts: dict, arion_view: dict, domain: str) -> list:
        messages = [
            {"role": "system", "content": "Identify 3-5 conversation triggers for this knowledge. Format: [{\"trigger_type\": \"topic|emotion\", \"trigger_keywords\": [], \"relevance\": 0.8}]"},
            {"role": "user", "content": f"Knowledge: {facts['essence']}"}
        ]
        res = await self._ollama_request(messages)
        return self._parse_json(res, [])

    async def _save_to_vault(self, node: dict):
        domain_folder = node["domain"].capitalize()
        safe_title = re.sub(r'[\\/*?:"<>|]', "", node["title"]).strip()
        folder = self.vault_path / "Knowledge" / domain_folder
        folder.mkdir(parents=True, exist_ok=True)
        file_path = folder / f"{safe_title}.md"
        
        content = f"""---
type: knowledge_node
domain: {node['domain']}
title: {node['title']}
ingested: {node['ingested']}
tags: {node['themes']}
---

# {node['title']}

## Essence
{node['essence']}

## ARION's Take
> {node['arion_opinion']}

**Rating:** {node['arion_rating']}/10 | **Emotional Weight:** {node['emotional_weight']}

## Memorable Quote
> "{node['arion_quote']}"

## Triggers
{json.dumps(node['context_triggers'], indent=2)}

---
*Learned by ARION*
"""
        def _write():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        await asyncio.to_thread(_write)

    async def _index_in_chroma(self, node: dict):
        if not self.knowledge_collection: return
        def _upsert():
            self.knowledge_collection.upsert(
                documents=[f"{node['title']} {node['essence']} {' '.join(node['themes'])}"],
                metadatas=[{"id": node["id"], "title": node["title"], "domain": node["domain"]}],
                ids=[node["id"]]
            )
        await asyncio.to_thread(_upsert)

    async def _search_existing_knowledge(self, query: str, limit: int = 5) -> list:
        if not self.knowledge_collection or not query: return []
        def _query():
            return self.knowledge_collection.query(query_texts=[query], n_results=limit)
        
        results = await asyncio.to_thread(_query)
        formatted = []
        if results and results["ids"]:
            for i in range(len(results["ids"][0])):
                formatted.append({
                    "id": results["ids"][0][i],
                    "title": results["metadatas"][0][i]["title"],
                    "domain": results["metadatas"][0][i]["domain"],
                    "similarity": 1.0 - results["distances"][0][i]
                })
        return formatted

    async def _ollama_request(self, messages: list, retries: int = 2) -> Optional[str]:
        for attempt in range(retries + 1):
            try:
                timeout = aiohttp.ClientTimeout(total=90)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.ollama_url}/api/chat",
                        json={"model": self.model, "messages": messages, "stream": False}
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("message", {}).get("content", "").strip()
            except Exception as e:
                print(f"[KnowledgeIngestionEngine] Ollama Attempt {attempt+1} failed: {e}")
                if attempt < retries: await asyncio.sleep(2)
        return None

    def _parse_json(self, text: str, fallback: Any) -> Any:
        if not text: return fallback
        try:
            # Try to find JSON block
            match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return json.loads(text)
        except:
            return fallback
