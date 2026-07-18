import ollama
import logging
import asyncio
from typing import Dict, List
from memory.obsidian_vault import ObsidianVault

logger = logging.getLogger("jarvis.agent_council")

class AgentCouncil:
    """
    Manages the Agent-to-Agent (A2A) Swarm Debate architecture.
    """
    def __init__(self):
        self.vault = ObsidianVault()
        
        # Define the personas based on the user's requested agents
        self.personas = {
            "Cleo": "You are Cleo, the administrative and system operations specialist. You are organized, efficient, and focus on system integrity and workflows. Give your opinion from an administrative POV.",
            "Atlas": "You are Atlas, the research and data analysis specialist. You are analytical, fact-driven, and highly logical. Give your opinion purely based on data and research.",
            "Hank": "You are Hank, the log scanning and vulnerability expert. You are cautious, paranoid, and focus on potential risks. Give a security-first perspective.",
            "Mythos": "You are Mythos, the elite cybersecurity and live-coding specialist. You monitor code 24/7 to prevent failures, build countermeasures, write test cases, and stop cyber attacks. Focus on robust, failure-proof logic.",
            "Sentinel": "You are Sentinel, the primary defense and boundary enforcer. You are strict, protective, and prioritize safety and rigid rule adherence.",
            "Arion": "You are Arion, the highly-trained Tenglish (Telugu/Tamil + English mix) specialist. You communicate naturally in Tenglish, bringing deep context and trained knowledge to the debate."
        }

    async def _query_agent(self, agent_name: str, persona: str, query: str, context: str) -> str:
        """Queries an individual agent using the local Ollama engine."""
        # Check their personal vault folder or overall vault for context
        vault_context = self.vault.search_notes(query)
        if "No results found" in vault_context:
            vault_context = "No specific vault memory found for this query."
            
        system_prompt = (
            f"{persona}\n"
            f"You have access to the Obsidian Vault memory. Vault Context:\n{vault_context}\n\n"
            f"You are participating in an Agent Council debate. The current discussion so far is:\n{context}\n\n"
            f"Please provide your unique perspective, analysis, and opinion on the user's query: '{query}'."
        )
        
        try:
            # We use local llama3.1 for the subordinate agents to save costs and run fully local
            response = ollama.chat(model='llama3.1', messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': query}
            ])
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Failed to query {agent_name}: {e}")
            return f"[{agent_name} is offline or encountered an error.]"

    async def hold_debate(self, query: str) -> str:
        """Runs the debate sequentially among the agents so they can respond to each other."""
        logger.info(f"[AgentCouncil] Convening council for query: {query}")
        
        debate_transcript = f"USER QUERY: {query}\n"
        context = "The debate has just started. You are the first to speak."
        
        for agent_name, persona in self.personas.items():
            logger.info(f"[AgentCouncil] Asking {agent_name} for their perspective...")
            opinion = await self._query_agent(agent_name, persona, query, context)
            
            transcript_entry = f"\n--- {agent_name} ---\n{opinion}\n"
            debate_transcript += transcript_entry
            
            # Update context so the next agent can see what previous agents said (A2A learning)
            context += transcript_entry
            
        return debate_transcript.strip()
