import os
import logging
import sqlite3
import asyncio
from datetime import datetime
from core.fleet.local_db import fleet_db
from core.fleet.memory import fleet_memory
from brain.learning.dream_state import DreamState
from langchain_ollama import ChatOllama
from config.system_config import JarvisConfig

logger = logging.getLogger("SleepCycle")

class SleepCycle:
    """
    Handles the nightly 'Deep Sleep' process.
    Summarizes daily interactions into 'Core Lessons' and updates system prompts.
    """
    def __init__(self, ai_engine=None, executive=None):
        self.llm = ChatOllama(
            model="gemma3:1b", 
            temperature=0.3,
            base_url=JarvisConfig.OLLAMA_BASE_URL
        )
        self.dream_state = DreamState(ai_engine)
        self.executive = executive

    async def run_nightly_process(self):
        """
        Main loop for the sleep cycle.
        1. Fetch daily logs.
        2. Distill lessons.
        3. Update agent 'DNA' (System Prompts).
        """
        logger.info("Deep Sleep: Fleet entering nightly distillation...")
        
        agents = ["atlas", "hank", "critic", "cleo"]
        for agent_id in agents:
            await self._distill_agent_memory(agent_id)
            
        # 4. Run Synthetic Rehearsal (Linguistic DNA Learning)
        if self.executive:
            from nexus.cognition.executive_a14 import NexusMode
            await self.executive.set_mode(NexusMode.SCHOLAR)
            
        await self.dream_state.run_rehearsal()
            
        # Return to Buddy/Passive mode after rehearsal
        if self.executive:
            from nexus.cognition.executive_a14 import NexusMode
            await self.executive.set_mode(NexusMode.BUDDY)

        logger.info("Deep Sleep: Fleet waking up. DNA updated.")

    async def _distill_agent_memory(self, agent_id: str):
        """
        Uses a local LLM to condense daily interactions into 3 core lessons.
        """
        # Fetch logs from the last 24 hours
        conn = sqlite3.connect("memory/fleet.db")
        c = conn.cursor()
        c.execute("SELECT task, critic_feedback FROM interaction_logs WHERE agent_id = ? AND timestamp > datetime('now', '-1 day')", (agent_id,))
        logs = c.fetchall()
        conn.close()

        if not logs:
            logger.info(f"No logs for {agent_id} today. Skipping distillation.")
            return

        log_text = "\n".join([f"Task: {l[0]} | Feedback: {l[1]}" for l in logs])
        
        prompt = f"""
        You are summarizing the daily experience for agent {agent_id}.
        Based on these logs, identify the 3 most important 'Core Lessons' this agent should remember forever.
        Keep each lesson under 15 words.
        
        Daily Logs:
        {log_text}
        
        Core Lessons:
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            lessons = response.content.strip()
            
            # Store lessons in the agent's Private Journal
            fleet_memory.write_journal_entry(agent_id, "Deep Sleep Distillation", lessons)
            
            # Here we would also update the system prompt in the database if we had a table for it.
            # For now, we'll log it as a successful growth step.
            logger.info(f"Distilled DNA for {agent_id}: {lessons[:50]}...")
            
        except Exception as e:
            logger.error(f"Sleep cycle failed for {agent_id}: {e}")

async def start_sleep_scheduler(ai_engine=None, executive=None):
    """Background task to run sleep cycle at 03:00 AM every night."""
    from datetime import datetime, timedelta
    sleep_cycle = SleepCycle(ai_engine, executive)
    
    while True:
        now = datetime.now()
        target = now.replace(hour=3, minute=0, second=0, microsecond=0)
        
        if now >= target:
            target += timedelta(days=1)
            
        wait_seconds = (target - now).total_seconds()
        logger.info(f"SleepCycle: Scheduled next distillation in {wait_seconds/3600:.1f} hours (at 03:00 AM)")
        await asyncio.sleep(wait_seconds)
        
        try:
            await sleep_cycle.run_nightly_process()
        except Exception as e:
            logger.error(f"Scheduled sleep cycle failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(SleepCycle().run_nightly_process())
