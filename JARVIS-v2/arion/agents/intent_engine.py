import asyncio
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

try:
    import aiohttp
except ImportError:
    aiohttp = None

class IntentEngine(BaseAgent):
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "qwen2.5-coder:7b"):
        super().__init__("IntentEngine", [Channel.INTENT])
        self.ollama_url = ollama_url
        self.model = model

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "extract_intent":
            text = message.payload.get("text", "")
            # MULTILINGUAL TIERED CLASSIFICATION
            intent_data = await self._analyze_tiered_intent(text)
            if message.requires_response:
                await self.respond_to(message, "intent_extracted", intent_data)

    async def _analyze_tiered_intent(self, text: str) -> dict:
        if not aiohttp:
            return {"tier": 1, "category": "unknown", "intent": "aiohttp missing"}

        # AGENT 4: INTENT + STYLE ENGINE
        # Operates exclusively on clean semantic English to bypass dialect confusion.
        prompt = f"""Analyze the following conversational English message.
Input Semantic Text: "{text}"

Your job is to determine how the AI should reply. Categorize the intent into the following JSON schema strictly.
Return JSON only:
{{
  "intent": "<short summary like 'casual_check_in', 'question', 'venting', 'joke', 'sarcasm'>",
  "emotion": "<happy / bored / frustrated / playful / sad / neutral>",
  "response_style": "<hype / comfort / banter / info / dismissive>",
  "dialect_to_reply_in": "<telugu / hindi / english>",
  "length": "<short / medium / long>",
  "tier": <number 1-5 where 1 is filler, 3 is normal, 5 is deeply emotional or hostile>
}}
"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json" # Ensure JSON output
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"{self.ollama_url}/api/generate", json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        raw_res = data.get("response", "{}").strip()
                        return self._parse_json(raw_res)
        except Exception as e:
            print(f"[IntentEngine] Analysis Error: {e}")
            
        return {"tier": 1, "category": "General", "intent": "Error in classifier"}

    def _parse_json(self, raw):
        import json
        try: return json.loads(raw)
        except: return {"tier": 1, "category": "General", "intent": raw[:50]}
