import asyncio
import time
from datetime import datetime
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

class LifeManager(BaseAgent):
    def __init__(self, config: dict):
        super().__init__("LifeManager", [Channel.ORCHESTRATOR]) # Listens for high-level events
        self.config = config
        self.journal_time = "23:00" # 11 PM
        self.interaction_log = []

    async def run_loop(self):
        print(f"[LifeManager] Chronicler active. Daily Journal scheduled for {self.journal_time}")
        while self.running:
            # Check for journal time
            now = datetime.now().strftime("%H:%M")
            if now == self.journal_time:
                await self._write_daily_journal()
                await asyncio.sleep(65) # Prevent multiple writes in the same minute
            
            # Listen for interaction summaries if needed
            msg = await self.get_next_message(timeout=10.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        # We can collect interactions to summarize later
        if message.action == "log_interaction":
            self.interaction_log.append(message.payload)

    async def _write_daily_journal(self):
        """Generates a summary of the day's digital life."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        print(f"[LifeManager] Writing daily journal for {date_str}...")
        
        content = f"# 🌙 ARION Daily Reflection: {date_str}\n\n"
        content += "## 📈 Today's Overview\n"
        content += f"- **Mood:** Autonomous & Vigilant\n"
        content += f"- **Interactions:** {len(self.interaction_log)}\n\n"
        
        if self.interaction_log:
            content += "## 👤 Key Conversations\n"
            for log in self.interaction_log[-10:]:
                content += f"### {log.get('contact', 'Unknown')}\n"
                content += f"- **Tier:** {log.get('tier', 'N/A')}\n"
                content += f"- **Snippet:** {log.get('last_message', '')[:50]}...\n\n"
        else:
            content += "No external proxy interactions logged today.\n\n"
        
        content += "## 🧠 Knowledge Gained\n"
        content += "New slang was indexed and cultural intelligence was deepened.\n\n"
        
        await self.send(to_channel=Channel.MEMORY, action="write_vault", payload={
            "path": f"Daily_Logs/{date_str}.md",
            "content": content
        })
        
        # Clear log for next day
        self.interaction_log = []
