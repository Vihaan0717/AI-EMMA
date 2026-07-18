import asyncio
import time
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message, Priority

try:
    import psutil
except ImportError:
    psutil = None

try:
    import GPUtil
except ImportError:
    GPUtil = None

class SystemMonitor(BaseAgent):
    def __init__(self):
        super().__init__("SystemMonitor", [Channel.SYSTEM_HEALTH, Channel.MONITOR])
        self.check_interval = 5.0
        self.critical_temp = 90.0
        self.critical_ram = 95.0
        
    async def run_loop(self):
        while self.running:
            if not psutil:
                await asyncio.sleep(self.check_interval)
                continue
                
            # Gather metrics
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            gpus = GPUtil.getGPUs() if GPUtil else []
            gpu_temp = max([g.temperature for g in gpus]) if gpus else 0.0
            gpu_load = max([g.load for g in gpus]) if gpus else 0.0
            
            if ram > self.critical_ram or gpu_temp > self.critical_temp:
                print(f"[SystemMonitor] CRITICAL VITAL: RAM={ram}% GPU_TEMP={gpu_temp}C")
                await self.send(
                    to_channel=Channel.TELEGRAM,
                    action="send_alert",
                    payload={"message": f"🚨 OVERLOAD! RAM: {ram}%, GPU temp: {gpu_temp}C"},
                    priority=Priority.CRITICAL
                )
                
            # Broadcast system vitals for Resource Governor
            await self.send(
                to_channel=Channel.BROADCAST,
                action="system_vitals",
                payload={
                    "cpu_percent": cpu,
                    "ram_percent": ram,
                    "disk_percent": disk,
                    "gpu_temp": gpu_temp,
                    "gpu_load": gpu_load,
                    "timestamp": time.time()
                },
                priority=Priority.LOW
            )
            
            # Since we just produce, we only need to sleep
            # Process any incoming requests (if any)
            msg = await self.get_next_message(timeout=self.check_interval)
            while msg:
                await self.handle_message(msg)
                msg = await self.get_next_message(timeout=0)
            
            if not msg:
                await asyncio.sleep(max(0, self.check_interval))

    async def handle_message(self, message: Message):
        if message.action == "get_vitals":
            if psutil:
                cpu = psutil.cpu_percent()
                await self.respond_to(message, "vitals_data", {"cpu": cpu})
        
        elif message.action == "get_status":
            chat_id = message.payload.get("chat_id")
            
            # 1. Request Agent Health Summary
            health_req = Message(
                from_agent=self.name,
                to_channel=Channel.AGENT_HEALTH,
                action="get_health_summary",
                requires_response=True
            )
            health_res = await self.bus.request(health_req, timeout=5.0)
            
            agent_list_text = ""
            if health_res and "agents" in health_res.payload:
                agents = health_res.payload["agents"]
                # Format: 🟢 AgentA | 🟡 AgentB
                items = []
                for a in agents:
                    icon = "🟢" if a["status"] == "ACTIVE" else "🟡"
                    items.append(f"{icon} {a['agent']}")
                agent_list_text = "\n" + " | ".join(items) if items else "\n*No agents reporting.*"
            
            # 2. Gather Vitals
            cpu = psutil.cpu_percent() if psutil else "N/A"
            ram = psutil.virtual_memory().percent if psutil else "N/A"
            gpu_res = "Healthy"
            
            status_text = (
                "🤖 *ARION System Status*\n"
                f"💻 CPU: `{cpu}%` | 🧠 RAM: `{ram}%`\n"
                f"🔥 GPU: `{gpu_res}`\n"
                f"📡 Bus: `Active` | 🕒 Up: `Healthy`"
                f"\n\n*Agents Reporting In:*{agent_list_text}"
            )
            
            if chat_id:
                await self.send(
                    to_channel=Channel.TELEGRAM,
                    action="send_reply",
                    payload={"text": status_text, "chat_id": chat_id}
                )
            else:
                await self.respond_to(message, "status_data", {"status": status_text})
