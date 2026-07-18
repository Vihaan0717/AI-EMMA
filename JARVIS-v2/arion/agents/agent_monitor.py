import time
import asyncio
from typing import Dict
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message, Priority

class AgentMonitor(BaseAgent):
    def __init__(self, config: dict):
        super().__init__("AgentMonitor", [Channel.AGENT_HEALTH, Channel.BROADCAST])
        self.heartbeats: Dict[str, float] = {}
        self.errors: Dict[str, list] = {}
        self.zombie_multiplier = config.get("zombie_multiplier", 3)
        self.dead_multiplier = config.get("dead_multiplier", 6)
        self.base_interval = config.get("heartbeat_interval_seconds", 10)
        self.current_cpu_load = 0.0
        
    async def run_loop(self):
        while self.running:
            msg = await self.get_next_message(timeout=5.0)
            if msg:
                await self.handle_message(msg)
            
            # Check for zombies
            now = time.time()
            # Adaptive multiplier: if CPU > 90%, double the zombie check time
            adaptive_zombie_mult = self.zombie_multiplier
            if self.current_cpu_load > 90.0:
                adaptive_zombie_mult *= 2.0

            for agent, last_beat in list(self.heartbeats.items()):
                delta = now - last_beat
                if delta > self.base_interval * self.dead_multiplier:
                    print(f"[AgentMonitor] ALARM: {agent} is DEAD! (Delta: {delta:.1f}s)")
                    await self._alert_telegram(f"🔥 AGENT DEAD: {agent}")
                    del self.heartbeats[agent]
                elif delta > self.base_interval * adaptive_zombie_mult:
                    # Only warn if it's not a known high-load spike
                    if self.current_cpu_load < 95.0 or delta > (self.base_interval * 10):
                        print(f"[AgentMonitor] WARNING: {agent} is a ZOMBIE. (Delta: {delta:.1f}s, CPU: {self.current_cpu_load}%)")

    async def handle_message(self, message: Message):
        if message.action == "heartbeat":
            agent = message.payload.get("agent")
            self.heartbeats[agent] = time.time()
        elif message.action == "system_vitals":
            self.current_cpu_load = message.payload.get("cpu_percent", 0.0)
        elif message.action == "agent_crash":
            agent = message.payload.get("agent")
            error = message.payload.get("error")
            if agent not in self.errors:
                self.errors[agent] = []
            self.errors[agent].append(error)
            await self._alert_telegram(f"❌ AGENT CRASHED: {agent}\nError: {error}")
            
        elif message.action == "get_health_summary":
            now = time.time()
            summary = []
            for agent, last_beat in self.heartbeats.items():
                delta = now - last_beat
                status = "ACTIVE"
                if delta > self.base_interval * self.zombie_multiplier:
                    status = "ZOMBIE"
                summary.append({"agent": agent, "status": status, "last_beat": round(delta, 1)})
            
            await self.respond_to(message, "health_summary", {"agents": summary})
            
    async def _alert_telegram(self, text: str):
        await self.send(
            to_channel=Channel.TELEGRAM,
            action="send_alert",
            payload={"message": text},
            priority=Priority.HIGH
        )
