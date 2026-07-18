import asyncio
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

class PredictionEngine(BaseAgent):
    def __init__(self):
        super().__init__("PredictionEngine", [Channel.PREDICTION])
        self.predictions_cache = {}
        self.is_paused = False

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "pause":
            self.is_paused = True
        elif message.action == "resume":
            self.is_paused = False
        elif message.action == "predict_next" and not self.is_paused:
            context = message.payload.get("context", "")
            predictions = ["What's next?", "Why?", "How does this work?"]
            if message.requires_response:
                await self.respond_to(message, "predictions", {"questions": predictions})
