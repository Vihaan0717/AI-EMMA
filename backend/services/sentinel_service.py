import asyncio
import aiohttp
import speech_recognition as sr
from core.logger import get_logger
from core.orchestrator import broadcast_alert

logger = get_logger("Sentinel")

class SentinelService:
    """
    Background Watchdog for JARVIS hardware and AI services.
    Self-heals or alerts the user if core components fail.
    """
    
    def __init__(self, check_interval=60):
        self.check_interval = check_interval
        self.running = False
        self._voice_cloner_url = "http://127.0.0.1:8768/health"
        self._last_voice_state = True
        self._last_mic_state = True

    async def _check_voice_cloner(self, session):
        """Check if XTTS server is alive via /health."""
        try:
            async with session.get(self._voice_cloner_url, timeout=5) as resp:
                if resp.status == 200:
                    if not self._last_voice_state:
                        logger.info("Sentinel: XTTS Voice Cloner has recovered.")
                        broadcast_alert("System Alert: Voice Cloner is back online, Sir.")
                    self._last_voice_state = True
                    return True
                else:
                    raise Exception(f"Status {resp.status}")
        except Exception as e:
            if self._last_voice_state:
                logger.error(f"Sentinel: XTTS Voice Cloner failure detected: {e}")
                broadcast_alert("⚠️ System Warning: I have lost my AI voice cloner. I will fall back to default speech.")
            self._last_voice_state = False
            return False

    async def _check_microphone(self):
        """Check if any working microphones are detected."""
        try:
            # list_microphone_names is sync, call in thread
            mics = await asyncio.to_thread(sr.Microphone.list_microphone_names)
            if not mics:
                if self._last_mic_state:
                    logger.error("Sentinel: No microphones detected!")
                    broadcast_alert("🚨 CRITICAL: I have lost all microphone connections. I am now deaf, Sir.")
                self._last_mic_state = False
                return False
            else:
                if not self._last_mic_state:
                    logger.info("Sentinel: Microphone connection restored.")
                    broadcast_alert("System Alert: Microphone connection restored. I can hear you again.")
                self._last_mic_state = True
                return True
        except Exception as e:
            logger.error(f"Sentinel: Mic check error: {e}")
            return False

    async def run(self):
        """Main sentinel monitor loop."""
        logger.info(f"Sentinel Watchdog starting... monitoring every {self.check_interval}s")
        self.running = True
        
        async with aiohttp.ClientSession() as session:
            while self.running:
                # 1. Check Voice Cloner
                await self._check_voice_cloner(session)
                
                # 2. Check Microphone
                await self._check_microphone()
                
                await asyncio.sleep(self.check_interval)

    def stop(self):
        self.running = False
        logger.info("Sentinel Watchdog stopping.")

# Singleton helper
sentinel = SentinelService()
