"""
NEXUS-X ULTIMATE - Main Entry Point
One Brain • Two Personalities • Zero Crashes

Also exports legacy compatibility shims (boot_sequence, foreground_loop, alert_queue)
that avatar_main.py depends on.
"""

import os
import asyncio
import logging
import queue
import signal
import sys
import time
import traceback
import argparse
from typing import Optional
from dotenv import load_dotenv

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# NEXUS Core Imports
from core.message_bus import MessageBus
from core.ai_engine import AIEngine
from memory.memory_manager import MemoryManager
from core.brain import NexusBrain
from core.whatsapp_bridge import WhatsAppBridge
from services.telegram_service import TelegramService
from services.call_service import CallService
from services.siren_service import SirenService
from search.web_brain import WebBrain
from search.autonomous_learner import AutonomousLearner
from brain.learning.passive_awareness import PassiveAwareness
from nexus.cognition.behavior_observer import BehaviorObserver
from nexus.agents.insight_agent import InsightAgent
from core.fleet.sleep_cycle import start_sleep_scheduler
from services.bridge_server import run_bridge_async
from services.instagram_monitor import InstagramMonitor
from services.voice_service import VoiceService
from core.proactive_agent import ProactiveScheduler
from vision.screen_monitor import ScreenMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("logs/nexus_core.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("NexusMain")
nexus_brain = None

# ═══════════════════════════════════════════════════════════════════════
# LEGACY COMPATIBILITY LAYER
# avatar_main.py requires these symbols from main.py
# They are implemented as stubs that integrate with the new NEXUS core.
# ═══════════════════════════════════════════════════════════════════════

# A thread-safe queue for background alerts (used by BackgroundBrain)
alert_queue: queue.Queue = queue.Queue()


def boot_sequence(speaker=None, guard=None, telegram_service=None) -> bool:
    """
    Legacy boot sequence stub.
    Performs the startup verification (biometric, greeting, etc.)
    Returns True if the system should continue, False to abort.
    """
    logger.info("Running NEXUS boot sequence...")

    try:
        # If biometric guard is enabled, run identity check
        if guard is not None:
            import os
            # Allow bypass for development
            bypass = os.getenv("SECURITY_BYPASS", "False").lower() == "true"
            if bypass:
                logger.warning("Security bypass active. Skipping biometric check.")
                return True

            logger.info("Running biometric identity verification...")
            status = guard.verify_identity()

            if status not in ("boss", "verified"):
                logger.error(f"Boot sequence failed: Identity not confirmed (status={status})")
                return False

            logger.info("Identity confirmed. Boot sequence passed.")
        else:
            logger.info("No biometric guard configured. Boot sequence passed.")

        # Speak greeting if speaker is available
        if speaker is not None:
            try:
                asyncio.run(_speak_greeting(speaker))
            except Exception as e:
                logger.warning(f"Greeting failed (non-fatal): {e}")

        return True

    except Exception as e:
        logger.error(f"Boot sequence error: {e}")
        return True  # Non-fatal: allow system to continue


async def _speak_greeting(speaker):
    """Async greeting helper."""
    await speaker.speak("NEXUS-X online. All systems nominal.")


async def foreground_loop(
    speaker=None,
    listener=None,
    background_brain=None,
    guard=None,
    telegram_service=None,
    skip_greeting: bool = False
):
    """
    Legacy foreground loop stub.
    Keeps the system alive and processes voice commands.
    """
    logger.info("Entering NEXUS foreground loop...")

    # Boot the core NEXUS system in the background
    system = NexusSystem()
    nexus_task = asyncio.create_task(system.run())

    try:
        while True:
            # Drain alert queue
            while not alert_queue.empty():
                try:
                    alert = alert_queue.get_nowait()
                    logger.info(f"Alert: {alert}")
                except queue.Empty:
                    break

            await asyncio.sleep(1)

    except asyncio.CancelledError:
        logger.info("Foreground loop cancelled.")
    finally:
        await system.stop()


# ═══════════════════════════════════════════════════════════════════════
# NEXUS-X CORE SYSTEM (New Architecture)
# ═══════════════════════════════════════════════════════════════════════

class NexusSystem:
    def __init__(self):
        self.bus = MessageBus()
        self.ai = AIEngine()
        self.memory = MemoryManager()
        self.whatsapp = None
        self.telegram = None
        self.calls = None
        self.siren = None
        self.brain = None
        self.web = None
        self.learner = None
        self.passive_awareness = None
        self.behavior_observer = None
        self.insight_agent = None
        self.instagram = None
        self.voice = None
        self.proactive = None
        self.screen_monitor = None
        self.running = False

    async def initialize(self):
        logger.info("Initializing NEXUS-X ULTIMATE Core...")
        
        # 0. Start Message Bus
        await self.bus.start()

        # 1. Initialize Memory
        await self.memory.initialize()

        # 2. Initialize AI Engine
        await self.ai.initialize()
        self.memory.set_embedder(self.ai)

        # 3. Initialize Telegram Service (The Security Channel)
        # Skip if in WHATSAPP-ONLY mode to avoid conflicts
        if os.getenv("WHATSAPP_ONLY", "false").lower() != "true":
            self.telegram = TelegramService()
            await self.telegram.start()
        else:
            logger.info("Skipping Telegram Service in WHATSAPP-ONLY mode.")

        # 4. Initialize Emergency Services
        self.calls = CallService()
        self.siren = SirenService()

        # 5. Initialize Web Brain & Autonomous Learner
        self.web = WebBrain()
        self.learner = AutonomousLearner(self.web, self.memory, self.ai)
        
        # Link Web Brain & AI Engine to Fleet Manager for researcher agents
        from core.fleet.manager import fleet_manager
        fleet_manager.set_web_brain(self.web)
        fleet_manager.ai_engine = self.ai
        fleet_manager.memory_manager = self.memory


        # 6. Initialize Brain with module references
        self.brain = NexusBrain({
            "bus": self.bus,
            "ai": self.ai,
            "memory": self.memory,
            "telegram": self.telegram,
            "calls": self.calls,
            "siren": self.siren,
            "web": self.web,
            "executive": None # Added below
        })
        
        # A14 Executive Layer
        from nexus.cognition.executive_a14 import ExecutiveA14
        self.executive = ExecutiveA14(fleet_manager)
        self.brain.modules['executive'] = self.executive
        
        global nexus_brain
        nexus_brain = self.brain

        if self.telegram:
            self.telegram.orchestrator = self.brain

        await self.brain.start()

        # 4. Initialize WhatsApp Bridge (enabled by default for command bridge)
        if os.getenv("WHATSAPP_ENABLED", "true").lower() == "true":
            self.whatsapp = WhatsAppBridge(self.bus, self.brain)
            await self.whatsapp.start()
            logger.info("[WhatsApp] Full Command Bridge initialized with @agent routing & /commands")
            
            # Start Health Watchdog
            try:
                from core.health_watchdog import HealthWatchdog
                self.watchdog = HealthWatchdog(self.whatsapp, self.brain)
                await self.watchdog.start()
                self.brain.modules['health_watchdog'] = self.watchdog
                logger.info("[HealthWatchdog] Routine and morning alert system started.")
            except Exception as we:
                logger.error(f"[HealthWatchdog] Failed to start: {we}")

        # 7. Initialize A13: Passive Awareness
        self.passive_awareness = PassiveAwareness(self.bus, scholar=self.brain.scholar)
        await self.passive_awareness.start()
        
        # 7.5 Initialize Behavior Observer
        self.behavior_observer = BehaviorObserver(brain=self.brain)
        self.brain.modules['behavior'] = self.behavior_observer
        await self.behavior_observer.start_proactive_loop()
        
        # 7.6 Initialize Insight Agent
        self.insight_agent = InsightAgent(self.brain)
        self.brain.modules['insight'] = self.insight_agent
        
        # 7.7 Initialize Instagram Monitor
        self.instagram = InstagramMonitor(self.bus)
        self.brain.modules['instagram'] = self.instagram
        await self.instagram.start()

        # 7.8 Initialize Voice Service (Real-time STT/TTS)
        if os.getenv("VOICE_ENABLED", "false").lower() == "true":
            self.voice = VoiceService(self.brain, self.bus)
            await self.voice.start()
        else:
            logger.info("Voice Service disabled via configuration.")

        # 8. Start A10: Nightly Sleep Cycle (Glymphatic Scholar Loop)
        # Run in background with a delay to let system stabilize
        async def delayed_start():
            await asyncio.sleep(30) # Wait 30s before starting heavy background tasks
            await self.learner.start()
            asyncio.create_task(start_sleep_scheduler(self.ai, self.executive))
            asyncio.create_task(self._atlas_secret_mission())
            asyncio.create_task(self._insight_loop())
            
            # Start Stage 1 Proactive Agency
            self.proactive = ProactiveScheduler(telegram_service=self.telegram)
            self.proactive.start()
            
            # Start Stage 2 Continuous Screen Awareness
            self.screen_monitor = ScreenMonitor(buffer_size=3, interval=5)
            self.screen_monitor.start()
            
        asyncio.create_task(delayed_start())

        # 10. Start Mobile Command Bridge (WebSocket Spine)
        if os.getenv("DISABLE_BRIDGE", "false").lower() != "true":
            api_port = int(os.getenv("API_PORT", 8000))
            asyncio.create_task(run_bridge_async(self.brain, port=api_port))
        else:
            logger.info("External bridge detected. Skipping internal bridge startup.")

        logger.info("NEXUS Core initialized and ready.")

    async def _insight_loop(self):
        """Periodically generates insights and proposes proactive actions."""
        logger.info("[Insight] Starting proactive pattern analysis loop...")
        while self.running:
            try:
                # Every 4 hours
                await asyncio.sleep(14400)
                if self.insight_agent:
                    insights = await self.insight_agent.generate_daily_insights()
                    for insight in insights:
                        await self.insight_agent.propose_action(insight)
            except Exception as e:
                logger.warning(f"Insight loop error: {e}")
            await asyncio.sleep(60)

    async def _atlas_secret_mission(self):
        """Atlas hunts for trending tech slang on the web periodically."""
        logger.info("[Mission] Atlas: Commencing Tech Slang Hunt...")
        while self.running:
            try:
                # Every 6 hours
                query = "latest Hyderabad tech slang and Telugu startup terms"
                results = await self.web.learn(query)
                logger.info(f"[Mission] Atlas found linguistic trends: {str(results)[:100]}...")
                # Future: Feed directly into A13 candidates
            except Exception as e:
                logger.warning(f"Atlas mission failed: {e}")
            await asyncio.sleep(21600)

    async def run(self):
        self.running = True
        await self.initialize()

        while self.running:
            await asyncio.sleep(1)

    async def _start_autonomous_loop(self):
        """Starts the learner with a delay to let the system stabilize."""
        await asyncio.sleep(30) # Wait 30s for boot stabilization
        await self.learner.run_forever()

    async def stop(self):
        logger.info("Shutting down NEXUS Core...")
        self.running = False
        if self.learner:
            await self.learner.stop()
        if self.web:
            await self.web.close()
        await self.memory.stop()
        await self.ai.close()
        if self.telegram:
            await self.telegram.stop()
        if self.voice:
            await self.voice.stop()
        if self.proactive:
            self.proactive.stop()
        if self.screen_monitor:
            self.screen_monitor.stop()


async def main():
    system = NexusSystem()

    # Handle signals
    loop = asyncio.get_running_loop()
    
    # Simple argument parsing
    parser = argparse.ArgumentParser(description="NEXUS-X ULTIMATE")
    parser.add_argument("--mode", type=str, default="full", help="Launch mode: full | whatsapp")
    args = parser.parse_args()
    
    if args.mode == "whatsapp":
        os.environ["WHATSAPP_ONLY"] = "true"
        os.environ["WHATSAPP_ENABLED"] = "true"
        logger.info("[Bridge] Launching in WHATSAPP-ONLY Mode")
        # You could implement focused initialization here
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(system.stop()))
        except NotImplementedError:
            pass  # Windows doesn't support add_signal_handler for all signals

    try:
        await system.run()
    except Exception as e:
        logger.critical(f"FATAL SYSTEM ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
