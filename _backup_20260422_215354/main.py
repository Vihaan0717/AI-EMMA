"""
NEXUS-X OMEGA - Master Boot Sequence
The most human-like AI system ever built locally
100% Free, 100% Local, 100% Autonomous
"""

import asyncio
import logging
import os
import sys
import signal
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── Logging Setup ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/nexus.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('NEXUS-OMEGA')

# ─── Boot Banner ──────────────────────────────────────────────────
BANNER = """
+----------------------------------------------------------+
|                                                          |
|          N E X U S - X   O M E G A                      |
|     The Human-Level AI System                           |
|                                                          |
|     (X) Think  (X) Talk  (X) Act  (X) Heal  (X) Grow    |
|     100% Free - 100% Local - 24/7/365                   |
|                                                          |
+----------------------------------------------------------+
"""

class NexusOmegaBootLoader:
    """
    Single unified boot sequence for NEXUS-X OMEGA
    Handles all startup, health checks, and recovery
    """

    def __init__(self):
        self.start_time = datetime.now()
        self.modules = {}
        self.is_running = False
        self.boot_errors = []
        self._create_directories()

    def _create_directories(self):
        """Create all required directories"""
        dirs = [
            "logs", "data", "data/chromadb",
            "data/learning_logs", "data/daily_reports",
            "data/self_improvements", "data/conversations",
            "knowledge_vault/Brain/Working",
            "knowledge_vault/Brain/ShortTerm",
            "knowledge_vault/Brain/Episodic",
            "knowledge_vault/Brain/Semantic",
            "knowledge_vault/Knowledge",
            "knowledge_vault/People",
            "config", "models", "temp"
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)

    def _check_prerequisites(self):
        """Check all prerequisites before boot"""
        logger.info("🔍 Checking prerequisites...")
        checks = {
            "Python 3.10+": sys.version_info >= (3, 10),
            "Ollama Available": self._check_ollama(),
            "Data Directory": Path("data").exists(),
            "Config Directory": Path("config").exists(),
        }
        all_good = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            logger.info(f"  {status} {check}")
            if not result:
                all_good = False
        return all_good

    def _check_ollama(self):
        """Check if Ollama is running"""
        try:
            import urllib.request
            urllib.request.urlopen(
                'http://localhost:11434/api/tags',
                timeout=3
            )
            return True
        except:
            return False

    async def boot_all_systems(self):
        """Boot all systems in correct order"""
        print(BANNER)
        logger.info("🚀 NEXUS-X OMEGA Booting...")

        if not self._check_prerequisites():
            logger.error("Prerequisites check failed!")
            logger.info("Starting Ollama...")
            try:
                subprocess.Popen(["ollama", "serve"])
            except:
                pass
            await asyncio.sleep(5)

        # Boot order matters - dependencies first
        boot_sequence = [
            ("Message Bus",      self._boot_message_bus),
            ("Memory System",    self._boot_memory),
            ("AI Engine",        self._boot_ai_engine),
            ("Language Engine",  self._boot_language),
            ("Intent Engine",    self._boot_intent),
            ("Tool Registry",    self._boot_tools),
            ("Voice System",     self._boot_voice),
            ("Vision System",    self._boot_vision),
            ("Self Healer",      self._boot_healer),
            ("Background Brain", self._boot_background),
            ("API Server",       self._boot_api),
            ("WhatsApp Bridge",  self._boot_whatsapp),
            ("Telegram Bot",     self._boot_telegram),
            ("Master Brain",     self._boot_master_brain),
        ]

        for name, boot_fn in boot_sequence:
            try:
                logger.info(f"  🔄 Booting {name}...")
                await boot_fn()
                logger.info(f"  ✅ {name} Online")
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.error(f"  ❌ {name} Failed: {e}")
                self.boot_errors.append((name, str(e)))

        self.is_running = True
        uptime = (datetime.now() - self.start_time).seconds
        logger.info(f"""
╔══════════════════════════════════════╗
║   ✅ NEXUS-X OMEGA FULLY ONLINE     ║
║   Boot Time: {uptime}s                    ║
║   Systems: {len(boot_sequence) - len(self.boot_errors)}/{len(boot_sequence)} Online          ║
║   Status: THINKING AND READY 🧠     ║
╚══════════════════════════════════════╝
        """)

    async def _boot_message_bus(self):
        from core.message_bus import MessageBus
        self.modules['bus'] = MessageBus()
        await self.modules['bus'].start()

    async def _boot_memory(self):
        from agents.memory_manager import MemoryManager
        self.modules['memory'] = MemoryManager()
        await self.modules['memory'].initialize()

    async def _boot_ai_engine(self):
        from core.free_ai_engine import FreeAIEngine
        self.modules['ai'] = FreeAIEngine()
        await self.modules['ai'].initialize()

    async def _boot_language(self):
        # Implementation skipped for now as we don't have the file yet
        pass

    async def _boot_intent(self):
        from core.intent_engine import IntentEngine
        self.modules['intent'] = IntentEngine()

    async def _boot_tools(self):
        # Registration logic will be in tool_registry.py
        pass

    async def _boot_voice(self):
        if os.getenv('VOICE_ENABLED', 'true').lower() == 'true':
            # Skip until voice_agent implementation
            pass

    async def _boot_vision(self):
        if os.getenv('VISION_ENABLED', 'true').lower() == 'true':
            # Skip until vision_agent implementation
            pass

    async def _boot_healer(self):
        from core.self_healer import SelfHealer
        self.modules['healer'] = SelfHealer(self.modules)
        asyncio.create_task(self.modules['healer'].run_forever())

    async def _boot_background(self):
        # Implementation skipped until background_brain is ready
        pass

    async def _boot_api(self):
        # Implementation skipped until interface/api is ready
        pass

    async def _boot_whatsapp(self):
        if os.getenv('WHATSAPP_ENABLED', 'false').lower() == 'true':
            pass

    async def _boot_telegram(self):
        token = os.getenv('TELEGRAM_TOKEN', '')
        if token:
            pass

    async def _boot_master_brain(self):
        from core.nexus_brain import NexusBrain
        self.modules['brain'] = NexusBrain(self.modules)
        asyncio.create_task(self.modules['brain'].run_forever())

    async def run_forever(self):
        """Keep system running 24/7/365"""
        await self.boot_all_systems()

        # Setup graceful shutdown
        loop = asyncio.get_event_loop()
        try:
            for sig in (signal.SIGTERM, signal.SIGINT):
                if sys.platform != 'win32':
                    loop.add_signal_handler(
                        sig,
                        lambda: asyncio.create_task(self.shutdown())
                    )
        except NotImplementedError:
            logger.warning("Signal handlers not fully supported on this platform")

        logger.info("🔄 NEXUS-X OMEGA Running 24/7...")
        while self.is_running:
            await asyncio.sleep(60)
            await self._health_pulse()

    async def _health_pulse(self):
        """Every minute health check"""
        if 'healer' in self.modules:
            await self.modules['healer'].pulse()

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("⚠️ Graceful shutdown initiated...")
        self.is_running = False

        # Save memory before shutdown
        if 'memory' in self.modules:
            # await self.modules['memory'].save_all()
            pass

        logger.info("✅ NEXUS-X OMEGA shutdown complete")
        sys.exit(0)


if __name__ == "__main__":
    nexus = NexusOmegaBootLoader()
    try:
        asyncio.run(nexus.run_forever())
    except KeyboardInterrupt:
        logger.info("Shutdown by user")
