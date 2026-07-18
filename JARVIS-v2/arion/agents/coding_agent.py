import asyncio
import os
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

class CodingAgent(BaseAgent):
    def __init__(self):
        super().__init__("CodingAgent", [Channel.CODING])
        self.sandbox_dir = "sandbox"
        os.makedirs(self.sandbox_dir, exist_ok=True)

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "execute_code":
            code = message.payload.get("code", "")
            # Validate unsafe
            if "os.system" in code or "shutil.rmtree" in code:
                if message.requires_response:
                    await self.respond_to(message, "execution_error", {"error": "Dangerous imports detected."})
                return
            
            # Execute in sandbox manually or via subprocess
            # Mock success
            if message.requires_response:
                await self.respond_to(message, "execution_success", {"output": "Mock execution succeeded."})
