import os
import logging
from datetime import datetime
from core.fleet.local_db import fleet_db

logger = logging.getLogger("FleetMemory")

class FleetMemory:
    """
    Manages the 'Private Journals' (Obsidian-ready) and the 'Sleep Cycle' for agents.
    """
    def __init__(self, journal_dir="knowledge_vault/fleet/"):
        self.journal_dir = journal_dir
        os.makedirs(self.journal_dir, exist_ok=True)

    def write_journal_entry(self, agent_id: str, topic: str, content: str):
        """
        Writes a 'Lesson Learned' or 'Experience' entry to the agent's private journal.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.journal_dir, f"{agent_id}_journal.md")
        
        mode = "a" if os.path.exists(file_path) else "w"
        with open(file_path, mode, encoding="utf-8") as f:
            if mode == "w":
                f.write(f"# {agent_id.upper()} PRIVATE JOURNAL\n\n")
            
            f.write(f"## {date_str} - {topic}\n")
            f.write(f"{content}\n\n")
            f.write("---\n\n")
            
        logger.info(f"FleetMemory: Updated journal for {agent_id}")

    async def sleep_cycle(self):
        """
        Simulates a sleep cycle by summarizing daily interactions into 'Core Memories'.
        """
        logger.info("FleetMemory: Starting Sleep Cycle summarization...")
        # In a real implementation, this would fetch all logs from fleet_db 
        # and use an LLM to condense them into a single 'Core Memory' entry.
        
        # Placeholder for summarization logic
        agents = ["atlas", "hank", "critic"]
        for agent in agents:
            corrections = fleet_db.get_recent_corrections(agent, limit=10)
            if corrections:
                summary = f"Summary of today's learning: {len(corrections)} corrections received."
                self.write_journal_entry(agent, "Daily Summary (Sleep Cycle)", summary)
        
        logger.info("FleetMemory: Sleep Cycle complete.")

# Global instance
fleet_memory = FleetMemory()
