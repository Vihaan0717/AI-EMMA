import asyncio
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

class DigitalTwin(BaseAgent):
    def __init__(self):
        super().__init__("DigitalTwin", [Channel.ORCHESTRATOR])

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "style_response":
            base_text = message.payload.get("text", "")
            persona = message.payload.get("persona", {})
            identity = message.payload.get("identity", {})
            relationship = message.payload.get("relationship", "stranger")
            
            # In a full deployment, this uses an LLM. Here we style statically.
            style = identity.get("texting_style", {}).get(relationship, "polite")
            styled_text = f"[Styled as {relationship}: {style}] {base_text}"
            
            if message.requires_response:
                await self.respond_to(message, "response_styled", {"text": styled_text})
