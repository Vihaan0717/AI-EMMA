import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("PersonaUpgrader")

class PersonaUpgrader:
    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        self.upgrades_path = Path("memory/agent_dynamic_upgrades.json")

    def _load_upgrades(self) -> Dict[str, Any]:
        if self.upgrades_path.exists():
            try:
                with open(self.upgrades_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading upgrades: {e}")
        return {}

    def _save_upgrades(self, upgrades: Dict[str, Any]):
        try:
            self.upgrades_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.upgrades_path, "w", encoding="utf-8") as f:
                json.dump(upgrades, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving upgrades: {e}")

    async def ingest_material(self, agent_id: str, content: str, source_type: str = "book") -> str:
        """
        Ingests content (e.g., YouTube transcript, book summary, article) and generates learned rules/skills
        specifically adapted for the agent using the AI engine.
        """
        agent_id = agent_id.lower()
        if not self.ai_engine:
            # Fallback to local Ollama if ai_engine is not linked
            from langchain_ollama import ChatOllama
            self.ai_engine = ChatOllama(model="llama3.1:latest", temperature=0.3)

        prompt = f"""
You are the NEXUS Persona Upgrader. Analyze the following {source_type} material and extract actionable skills, behavioral guidelines, or advanced slangs/knowledge that the agent '{agent_id}' can adopt to improve their performance.

MATERIAL:
\"\"\"
{content[:8000]}
\"\"\"

Task:
Generate a structured JSON output with:
1. "insights": A single paragraph summary of new rules or concepts.
2. "skills": A dictionary of new/updated skills and their description/level.
3. "system_prompt_addition": Bullet points of system prompt guidelines to append.
"""

        try:
            # Check if ai_engine is the custom AIEngine or Langchain ChatOllama
            if hasattr(self.ai_engine, "generate"):
                response = await self.ai_engine.generate(prompt=prompt, system="You are a cognitive enhancement system.", temperature=0.3)
            else:
                from langchain_core.prompts import ChatPromptTemplate
                chain = ChatPromptTemplate.from_messages([("system", "You are a cognitive enhancement system."), ("user", "{input}")]) | self.ai_engine
                res = await chain.ainvoke({"input": prompt})
                response = res.content

            # Parse JSON response
            import re
            json_match = re.search(r"({.*})", response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                # Fallback simple parsing
                data = {
                    "insights": "Learned from external material.",
                    "skills": {"knowledge_ingestion": "advanced"},
                    "system_prompt_addition": f"- Apply insights from the ingested {source_type} content."
                }

            # Update agent upgrades
            upgrades = self._load_upgrades()
            if agent_id not in upgrades:
                upgrades[agent_id] = {"learned_prompt": "", "skills": {}}

            existing_prompt = upgrades[agent_id].get("learned_prompt", "")
            addition = data.get("system_prompt_addition", "")
            if isinstance(addition, list):
                addition = "\n".join(addition)
            
            upgrades[agent_id]["learned_prompt"] = existing_prompt + f"\n- [{source_type.upper()}]: {addition}"
            upgrades[agent_id]["skills"].update(data.get("skills", {}))

            self._save_upgrades(upgrades)
            logger.info(f"Successfully upgraded persona of agent: {agent_id}")
            return f"Agent {agent_id} successfully upgraded with {source_type} learning."
        except Exception as e:
            logger.error(f"Failed to ingest material for agent {agent_id}: {e}")
            return f"Failed to upgrade agent {agent_id}: {str(e)}"
