import asyncio
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

class EmotionEngine(BaseAgent):
    def __init__(self):
        super().__init__("EmotionEngine", [Channel.EMOTION])
        self.current_agent_emotion = "neutral"

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "analyze_emotion":
            text = message.payload.get("text", "")
            emotion = await self._analyze(text)
            if message.requires_response:
                await self.respond_to(message, "emotion_analyzed", {"emotion": emotion})

    async def _analyze(self, text: str) -> str:
        # Mock analysis; ideally would use an LLM call or dedicated emotion model
        t = text.lower()
        if "hate" in t or "angry" in t: return "anger"
        if "sad" in t or "cry" in t: return "sadness"
        if "happy" in t or "joy" in t or "yay" in t: return "joy"
        return "neutral"
