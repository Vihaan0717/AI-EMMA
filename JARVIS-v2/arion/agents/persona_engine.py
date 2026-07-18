import json
import asyncio
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

class PersonaEngine(BaseAgent):
    def __init__(self, core_path: str, adaptive_path: str):
        super().__init__("PersonaEngine", [Channel.PERSONA])
        self.core_path = core_path
        self.adaptive_path = adaptive_path
        self.core_persona = self._load_json(core_path)
        self.adaptive_persona = self._load_json(adaptive_path)

    def _load_json(self, path: str) -> dict:
        import os
        candidates = [path, f"arion/{path}"]
        for p in candidates:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception:
                    pass
        return {}

    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "get_persona":
            # Combine core and adaptive based on logic
            combined = {
                "core": self.core_persona,
                "adaptive": self.adaptive_persona
            }
            if message.requires_response:
                await self.respond_to(message, "persona_data", combined)
                
        elif message.action == "update_adaptive":
            updates = message.payload.get("updates", {})
            self._apply_updates(updates)
            
    def _apply_updates(self, updates: dict):
        for k, v in updates.items():
            if k not in self.core_persona:
                self.adaptive_persona[k] = v
        # Write back logic can be added here
