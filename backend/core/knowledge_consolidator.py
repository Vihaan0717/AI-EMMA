import os
import json
import sqlite3
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Tuple

from core.ai_engine import AIEngine
from search.web_brain import WebBrain
from brain.neurons.neural_graph import NeuralGraph
from brain.neurons.neuron import Neuron, NeuronType, MemoryLayer
from brain.neurons.synapse import Synapse, SynapseType

logger = logging.getLogger("KnowledgeConsolidator")

class KnowledgeConsolidator:
    """
    Cognitive system for proactive learning:
    - Extracts topics of interest from recent chat history and user profile.
    - Scrapes multiple web sources using WebBrain (Wikipedia, arXiv, stackoverflow, web).
    - Cross-checks facts using LLM reasoning to filter out noise, marketing fluff, and contradictions.
    - Saves verified, high-quality concepts into the neural graph memory.
    """
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.db_path = self.root / "memory" / "fleet.db"
        self.memory_json_path = self.root / "memory.json"
        
        # Core engines
        self.ai = AIEngine()
        self.web = WebBrain()
        self.graph = NeuralGraph()
        
    async def initialize(self):
        """Pre-warm AI engine connection"""
        await self.ai.initialize()
        
    async def run_consolidation_cycle(self) -> List[str]:
        """Runs the entire proactive learning loop"""
        logger.info("Starting Proactive Knowledge Consolidation cycle...")
        
        # 1. Extract topics from recent logs and user details
        topics = await self._extract_learning_topics()
        if not topics:
            logger.info("No learning topics identified in recent history.")
            return []
            
        logger.info(f"Identified potential learning topics: {topics}")
        learned_topics = []
        
        # 2. Query, Cross-Check, and Commit each topic
        for topic in topics:
            try:
                # Skip if already a strong, confirmed neuron in long term memory
                existing = self.graph.get_neuron(topic)
                if existing and existing.memory_layer == MemoryLayer.LONG_TERM and existing.confirmed_by_user:
                    logger.debug(f"Topic '{topic}' is already a mature long-term memory. Skipping.")
                    continue
                    
                # Fetch multi-source context
                logger.info(f"Gathering cross-source data for: '{topic}'")
                search_data = await self.web.learn(topic)
                if not search_data:
                    logger.warning(f"Could not fetch search data for '{topic}'")
                    continue
                    
                # Cross-verify facts
                logger.info(f"Cross-checking and validating info for: '{topic}'")
                verified_fact = await self._cross_verify_topic(topic, search_data)
                
                if verified_fact and verified_fact.get("trust_score", 0.0) >= 0.70:
                    # Save to Neural Graph
                    self._commit_to_memory(topic, verified_fact)
                    learned_topics.append(topic)
                else:
                    logger.warning(f"Topic '{topic}' failed validation (Trust Score: {verified_fact.get('trust_score', 0.0)}). Bloat/noise filtered out.")
            except Exception as e:
                logger.error(f"Error processing topic '{topic}': {e}")
                
        logger.info(f"Consolidation cycle completed. Newly consolidated knowledge: {learned_topics}")
        return learned_topics
        
    async def _extract_learning_topics(self) -> List[str]:
        """Identifies promising learning keywords based on chat history and profile facts"""
        chat_queries = []
        
        # Fetch from fleet DB logs
        if self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("SELECT task FROM interaction_logs ORDER BY timestamp DESC LIMIT 30")
                rows = c.fetchall()
                chat_queries = [r[0] for r in rows if r[0]]
                conn.close()
            except Exception as e:
                logger.error(f"Failed to read fleet DB: {e}")
                
        # Fetch from memory.json
        boss_facts = []
        if self.memory_json_path.exists():
            try:
                with open(self.memory_json_path, "r", encoding="utf-8") as f:
                    mem_data = json.load(f)
                    boss_facts = mem_data.get("facts", [])
            except Exception as e:
                logger.error(f"Failed to read memory.json: {e}")
                
        # Prompt LLM to identify high-value research topics
        prompt = f"""
Analyze the following recent user inputs and boss profile facts.
Identify up to 2 specific technical concepts, historical figures, educational topics, programming libraries, or nouns that are worth proactively researching to improve the system's response quality.
Focus on topics that are highly relevant to the boss's daily interests, programming, and learning.
Do NOT output greetings, conversational chatter, or generic verbs.

Recent User Chats:
{json.dumps(chat_queries[:15], indent=2)}

Boss Profile Facts:
{json.dumps(boss_facts, indent=2)}

Return ONLY a clean JSON list of strings representing the search terms.
Example: ["Vite dev server", "Neuroplasticity", "APJ Abdul Kalam"]
"""
        import random
        core_scientific_domains = [
            "botany plant hormones", "human brain neuroanatomy", "quantum wave function",
            "general relativity space-time", "schrodinger equation quantum mechanics",
            "eulers identity formula", "newtons laws of motion", "photosynthesis light reactions",
            "cellular respiration biology", "pythagorean theorem derivation", "maxwells equations electromagnetism"
        ]
        
        response = await self.ai.generate(prompt=prompt, temperature=0.2)
        extracted_topics = []
        try:
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end != -1:
                extracted_topics = json.loads(response[start:end])
                extracted_topics = [t.strip() for t in extracted_topics if isinstance(t, str) and len(t.strip()) > 2]
        except Exception as e:
            logger.warning(f"Failed to parse topic extraction JSON: {e}. Raw response: {response}")
            
        # Proactively inject 1 deep scientific domain/formula per cycle to learn
        injected_domain = random.choice(core_scientific_domains)
        if injected_domain not in extracted_topics:
            extracted_topics.append(injected_domain)
            
        return extracted_topics[:3]
        
    async def _cross_verify_topic(self, topic: str, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to compare multiple web documents, filter out marketing/fluff, and extract verified facts"""
        sources_text = ""
        
        # Wikipedia summary format
        if search_data.get("source") == "wikipedia":
            sources_text += f"Source: Wikipedia (Trust: 0.95)\nContent: {search_data.get('content', '')[:2000]}\n\n"
        elif "documents" in search_data:
            for idx, doc in enumerate(search_data["documents"][:4]):
                url = doc.get("url", "Web result")
                text = doc.get("text", "")[:800]
                sources_text += f"Source {idx+1}: {url} (Trust: 0.60)\nContent: {text}\n\n"
        elif search_data.get("source") == "arxiv":
            for idx, paper in enumerate(search_data.get("papers", [])[:3]):
                sources_text += f"Academic Source {idx+1}: arXiv (Trust: 0.95)\nTitle: {paper.get('title')}\nAbstract: {paper.get('summary')[:800]}\n\n"
        elif search_data.get("source") == "github":
            for idx, repo in enumerate(search_data.get("repos", [])[:3]):
                sources_text += f"Code Source {idx+1}: GitHub (Trust: 0.85)\nName: {repo.get('name')}\nDescription: {repo.get('description')}\n\n"
                
        if not sources_text:
            return {}
            
        system_prompt = """
You are the NEXUS-X Master Knowledge Archivist.
Your goal is to digest information from multiple web sources about a specific concept, cross-verify it for consistency, filter out marketing fluff/noise, and synthesize a set of bulletproof, confirmed facts.

CRITICAL MATHEMATICAL & SCIENTIFIC RIGOR:
- If the concept involves a mathematical formula, equation, theorem, or scientific law (e.g., Schrödinger equation, Euler's identity):
  * Double-check every variable, constant, and symbol.
  * Verify the derivation and mathematical correctness.
  * Ensure the explanation describes how each variable behaves.
  * If there is any inconsistency or mathematical hallucination between sources, drop the trust_score to 0.0 to prevent bad memory injection.
- Only output a valid JSON block containing:
{
  "description": "A verified, concise explanation of the concept or formula (1-3 sentences).",
  "facts": ["Key verified fact 1", "Key verified fact 2", "Key verified fact 3"],
  "formula": "The exact mathematical representation (optional, e.g. e^(i*pi) + 1 = 0)",
  "variables": {"symbol": "meaning"} (optional),
  "trust_score": 0.85
}
Do not include any surrounding markdown block or conversational text.
"""
        prompt = f"""
Concept: {topic}

Retrieved Web Sources:
{sources_text}

Extract clean, cross-verified, high-quality knowledge.
"""
        response = await self.ai.generate(prompt=prompt, system=system_prompt, temperature=0.1, is_heavy=True)
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(response[start:end])
        except Exception as e:
            logger.warning(f"Failed to parse cross-verification JSON: {e}. Raw response: {response}")
            
        return {}
        
    def _commit_to_memory(self, topic: str, fact: Dict[str, Any]):
        """Persist verified fact directly into the neural graph"""
        logger.info(f"Committing cross-verified concept '{topic}' to Neural Graph memory.")
        
        # 1. Get or create the main neuron
        neuron = self.graph.get_or_create_neuron(
            label=topic,
            neuron_type=NeuronType.CONCEPT,
            data={
                "description": fact.get("description", ""),
                "facts": fact.get("facts", []),
                "formula": fact.get("formula", ""),
                "variables": fact.get("variables", {}),
                "trust_score": fact.get("trust_score", 0.5),
                "last_consolidated": datetime.now().isoformat()
            }
        )
        
        # 2. Promote memory strength and layer
        neuron.strength = max(neuron.strength, 0.75)
        neuron.memory_layer = MemoryLayer.LONG_TERM
        neuron.confirmed_by_user = False  # Mark as system-learned, awaiting final user confirmation if queried
        
        # 3. Connect new concept to Owner (establishing associative connection)
        self.graph.connect(
            from_label=topic,
            to_label="Owner",
            synapse_type=SynapseType.CO_OCCURRED,
            bidirectional=True,
            initial_weight=fact.get("trust_score", 0.5)
        )
        
        # 4. Fire the neuron to establish activation pathways
        neuron.fire(boost=0.1)
        self.graph._save()
        logger.info(f"Concept '{topic}' successfully committed to memory graph.")
        
from datetime import datetime
