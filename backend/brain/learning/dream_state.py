import logging
import random
import asyncio
import os
import psutil
from brain.learning.learner import NexusLearner
from langchain_ollama import ChatOllama
from config.system_config import JarvisConfig

logger = logging.getLogger("DreamState")

class DreamState:
    """
    A10-A11 Sandbox 'Glymphatic Scholar Loop'.
    Autonomous nightly rehearsal where NEXUS-X 'practices walking' with new slang.
    """
    def __init__(self, ai_engine=None):
        self.learner = NexusLearner()
        self.ai = ai_engine # Should be the master AIEngine with Gemini access
        self.simulation_llm = ChatOllama(
            model="llama3.2:1b", # Ultra-fast for mass variations
            temperature=0.9,     
            base_url=JarvisConfig.OLLAMA_BASE_URL
        )
        self.critic_llm = ChatOllama(
            model="qwen2.5-coder:1.5b", # Strong logic for criticism
            temperature=0.1,
            base_url=JarvisConfig.OLLAMA_BASE_URL
        )

    async def run_rehearsal(self):
        """Main rehearsal loop (The Nightly Scholar Cycle)."""
        logger.info("🌌 NEXUS-X entering A10 Glymphatic Rehearsal (Walking Simulation)...")
        
        # A12: Check hardware health before starting intensive simulation
        if not self._check_hardware_safety():
            logger.warning("A12 Guard: CPU too hot/loaded. Postponing simulation.")
            return

        discovery = self.learner.get_discovery_list()
        if not discovery:
            logger.info("No new linguistic candidates to verify.")
            return

        for phrase in discovery:
            # A11: Verify with Scholar (Gemini API)
            await self._verify_with_scholar(phrase)
            
            # A10: The Walking Simulation
            await self._run_walking_simulation(phrase)
            
        logger.info("🌅 Scholar Cycle complete. DNA Registry hardened.")

    def _check_hardware_safety(self) -> bool:
        """A12 Hardware Guard: Prevent overheating during local LLM mass-inference."""
        cpu_usage = psutil.cpu_percent(interval=1)
        # Mock temp check since standard psutil doesn't always have it on Windows without WMI
        if cpu_usage > 70:
            return False
        return True

    async def _verify_with_scholar(self, phrase):
        """A11: Uses Gemini API to fetch official definitions and dialect accuracy."""
        if not self.ai: return
        
        logger.info(f"[A11] Scholar: Verifying '{phrase}' via Gemini...")
        prompt = f"Verify this Hyderabad/Deccani slang: '{phrase}'. Provide its literal meaning, social tier, and common usage."
        
        try:
            verification = await self.ai.generate(prompt, use_fast=False) # Use Gemini for high-accuracy
            logger.info(f"[A11] Verified DNA: {verification[:100]}...")
            # In a real setup, we'd update the DNA registry with this 'Golden' definition
        except Exception as e:
            logger.error(f"Scholar verification failed for {phrase}: {e}")

    async def _run_walking_simulation(self, phrase):
        """A10: Executes the Multi-Agent Peer-Review Loop for the phrase."""
        dna_entry = self._find_dna_entry(phrase)
        if not dna_entry: return

        meaning = dna_entry.get("meaning", "unknown")
        
        from core.fleet.manager import fleet_manager
        
        logger.info(f"🌙 A10 Scholar Loop: Starting Collaborative Peer-Review for '{phrase}'...")
        
        try:
            # Trigger the full fleet orchestration
            result = await fleet_manager.scholar_peer_review(phrase, meaning)
            
            logger.info(f"[A10] Peer-Review Result for '{phrase}': Score={result['score']} | Verdict={result['feedback'][:100]}...")
            
            if result["score"] > 85:
                # Reinforce DNA
                self.learner.learn(phrase, meaning, context="slang_verified", dialect=dna_entry.get("dialect", "General"))
        except Exception as e:
            logger.error(f"Scholar Peer-Review failed for {phrase}: {e}")

    def _find_dna_entry(self, phrase):
        for registry in self.learner.dna.values():
            if phrase in registry:
                return registry[phrase]
        return None

if __name__ == "__main__":
    import asyncio
    ds = DreamState()
    # asyncio.run(ds.run_rehearsal())
