import asyncio
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

class ResourceGovernor(BaseAgent):
    def __init__(self):
        super().__init__("ResourceGovernor", [Channel.BROADCAST])
        self.tier1_limit = 80.0  # Mild: Pause background tasks
        self.tier2_limit = 90.0  # Heavy: Pause secondary inference
        self.tier3_limit = 95.0  # Critical: Pause heavy hardware (Voice Inference)
        self.paused_agents = set()
        
    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "system_vitals":
            vitals = message.payload
            cpu = vitals.get("cpu_percent", 0)
            ram = vitals.get("ram_percent", 0)
            
            # --- Tier 1: Mild Overload (>80%) ---
            if cpu > self.tier1_limit:
                if "prediction_engine" not in self.paused_agents:
                    print(f"[ResourceGov] TIER 1 Overload ({cpu}%). Pausing PredictionEngine.")
                    await self._send_pause(Channel.PREDICTION, "prediction_engine")
            
            # --- Tier 2: Heavy Overload (>90%) ---
            if cpu > self.tier2_limit:
                if "comprehension_engine" not in self.paused_agents:
                    print(f"[ResourceGov] TIER 2 Overload ({cpu}%). Pausing LLM-Comprehension.")
                    await self._send_pause(Channel.COMPREHENSION, "comprehension_engine")
                if "intake_watcher" not in self.paused_agents:
                    await self._send_pause(Channel.INTAKE, "intake_watcher")

            # --- Tier 3: Critical Overload (>95%) ---
            if cpu > self.tier3_limit:
                if "voice_engine" not in self.paused_agents:
                    print(f"[ResourceGov] TIER 3 CRITICAL ({cpu}%). Pausing Voice Inference.")
                    await self._send_pause(Channel.VOICE, "voice_engine", action="pause_inference")

            # --- Recovery Logic ---
            if cpu < (self.tier1_limit - 10):
                await self._check_recovery(cpu)

    async def _send_pause(self, channel, agent_id, action="pause"):
        await self.send(
            to_channel=channel,
            action=action,
            payload={"reason": "system overload", "cpu_limit": self.tier1_limit}
        )
        self.paused_agents.add(agent_id)

    async def _check_recovery(self, cpu):
        if not self.paused_agents:
            return

        # Gradual recovery
        to_recover = list(self.paused_agents)
        for agent_id in to_recover:
            channel = self._get_channel_for_agent(agent_id)
            action = "resume_inference" if agent_id == "voice_engine" else "resume"
            
            print(f"[ResourceGov] System recovered ({cpu}%). Resuming {agent_id}.")
            await self.send(to_channel=channel, action=action, payload={})
            self.paused_agents.remove(agent_id)

    def _get_channel_for_agent(self, agent_id):
        mapping = {
            "prediction_engine": Channel.PREDICTION,
            "comprehension_engine": Channel.COMPREHENSION,
            "intake_watcher": Channel.INTAKE,
            "voice_engine": Channel.VOICE
        }
        return mapping.get(agent_id, Channel.BROADCAST)
