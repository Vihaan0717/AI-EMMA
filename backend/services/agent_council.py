import os
import sys
import ollama
import logging
import asyncio
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from memory.obsidian_vault import ObsidianVault

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.agent_result import AgentResult
from core.agent_message import AgentMessage
from core.agent_bus import AgentBus
import json

logger = logging.getLogger("jarvis.agent_council")

class CapabilityManager(BaseModel):
    name: str
    prompt: str
    tools: List[str] = Field(default_factory=list)
    policies: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    memory_namespace: str
    evaluation_suite: str = "default_suite"

class AgentCouncil:
    """
    Manages the Agent-to-Agent (A2A) Swarm Debate architecture.
    """
    def __init__(self):
        self.vault = ObsidianVault()
        self.bus = AgentBus()
        
        # Define the specialized capability managers based on the user's requested agents
        self.managers: Dict[str, CapabilityManager] = {
            "Cleo": CapabilityManager(
                name="Cleo", 
                prompt="Administrative and system operations specialist. Focus on workflows.",
                tools=["os_execute", "os_file_read"],
                policies=["strict_logging", "no_destructive_commands"],
                memory_namespace="PRIVATE_CLEO"
            ),
            "Atlas": CapabilityManager(
                name="Atlas", 
                prompt="Research and data analysis specialist. Analytical and fact-driven.",
                tools=["atlas_search_web", "verify_sources"],
                policies=["require_3_sources", "cite_references"],
                memory_namespace="PRIVATE_ATLAS"
            ),
            "Hank": CapabilityManager(
                name="Hank", 
                prompt="Log scanning and vulnerability expert. Cautious and paranoid.",
                tools=["scan_security_logs"],
                policies=["deny_network_access", "alert_on_anomaly"],
                memory_namespace="PRIVATE_HANK"
            ),
            "Mythos": CapabilityManager(
                name="Mythos", 
                prompt="Elite cybersecurity and live-coding specialist. Focus on failure-proof logic.",
                tools=["review_code", "write_tests"],
                policies=["enforce_test_coverage"],
                memory_namespace="PRIVATE_MYTHOS"
            ),
            "Sentinel": CapabilityManager(
                name="Sentinel", 
                prompt="Primary defense and boundary enforcer. Strict rule adherence.",
                tools=["block_action"],
                policies=["deny_by_default"],
                memory_namespace="PRIVATE_SENTINEL"
            ),
            "Arion": CapabilityManager(
                name="Arion", 
                prompt="Highly-trained Tenglish specialist. Bring deep context to debates.",
                tools=["translate"],
                policies=[],
                memory_namespace="PRIVATE_ARION"
            )
        }

    async def _query_agent(self, agent_name: str, persona: str, query: str, context: str) -> AgentMessage:
        """Queries an individual agent using the local Ollama engine and returns an AgentMessage."""
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
            # We use local qwen2.5-coder:7b for the subordinate agents to save costs and run fully local
            response = ollama.chat(model='qwen2.5-coder:7b', messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': query}
            ])
            content = response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Failed to query {agent_name}: {e}")
            content = f"[{agent_name} is offline or encountered an error.]"

        msg = AgentMessage(
            conversation_id="council_debate",
            sender=agent_name,
            recipient="nexus",
            message_type="RESEARCH_FINDING",
            topic=query[:50],
            content=content,
            confidence=0.85
        )
        
        try:
            self.bus.send(msg)
        except Exception as e:
            logger.error(f"Failed to persist message to AgentBus: {e}")
            
        return msg

    async def hold_debate(self, query: str) -> str:
        """Runs the debate sequentially among the agents so they can respond to each other."""
        logger.info(f"[AgentCouncil] Convening council for query: {query}")
        
        context = "The debate has just started. You are the first to speak."
        messages = []
        
        for agent_name, manager in self.managers.items():
            logger.info(f"[AgentCouncil] Asking {agent_name} for their perspective...")
            agent_msg = await self._query_agent(agent_name, manager.prompt, query, context)
            messages.append(agent_msg)
            
            transcript_entry = f"\n--- {agent_name} ---\n{agent_msg.content}\n"
            
            # Update context so the next agent can see what previous agents said (A2A learning)
            context += transcript_entry
            
        attributions = [
            {
                "speaker": msg.sender, 
                "message_id": msg.message_id, 
                "claim": msg.content[:100] + "...", 
                "confidence": msg.confidence
            }
            for msg in messages
        ]
        
        full_transcript = "\n\n".join([f"[{m.sender}] (msg_id: {m.message_id}):\n{m.content}" for m in messages])
        result_data = {
            "transcript": full_transcript,
            "attributions": attributions
        }
        
        return AgentResult(
            status="success",
            confidence=0.8,
            sources=["Cleo", "Atlas", "Hank", "Mythos", "Sentinel", "Arion"],
            answer=json.dumps(result_data, indent=2),
            needs_verification=False,
            errors=[]
        ).to_json()

    async def call_council(self, topic: str, context: str) -> str:
        """Invokes a debate among the capability managers."""
        logger.info(f"Calling the Agent Council for topic: {topic}")
        
        tasks = []
        for name, manager in self.managers.items():
            tasks.append(self._query_agent(name, manager.prompt, topic, context))
            
        responses = await asyncio.gather(*tasks)
        
        combined_response = "\n\n".join([f"[{r.sender}]: {r.content}" for r in responses])
        return combined_response
