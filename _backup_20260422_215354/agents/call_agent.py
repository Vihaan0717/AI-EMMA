import asyncio
import time
from core.logger import get_logger
from agents.response_agent import mirror_engine
from config.system_config import JarvisConfig

logger = get_logger("CallAgent")

class TelephonyAgent:
    """
    JARVIS Call Intelligence Layer.
    Handles 'Call Lifting' and answering with 100% human mirroring.
    """
    def __init__(self, telegram_service=None):
        self.telegram = telegram_service
        self.is_on_call = False
        logger.info("Telephony Agent active. Monitoring mobile edge for calls...")

    async def monitor_incoming_calls(self):
        """Continuously polls the mobile edge for incoming call status."""
        import requests
        while True:
            if not self.is_on_call:
                try:
                    # Check cloud status for 'incoming_call' job results or raw state
                    # For this implementation, we assume termux_sync reports call state
                    url = f"{JarvisConfig.RENDER_URL}/get_call_state"
                    res = requests.get(url, timeout=5)
                    if res.status_code == 200:
                        state = res.json()
                        if state.get("incoming"):
                            caller = state.get("number", "Unknown")
                            logger.info(f"🚨 INCOMING CALL DETECTED: {caller}")
                            await self.handle_call(caller)
                except Exception as e:
                    pass
            await asyncio.sleep(5)

    async def handle_call(self, caller: str):
        """Autonomous Call Lifting & Human-like Interaction."""
        import requests
        self.is_on_call = True
        logger.info(f"Lifting call from {caller}...")
        
        # 1. Trigger Physical Answer on Phone
        requests.post(f"{JarvisConfig.RENDER_URL}/add_job", json={
            "target": "mobile", "type": "answer_call", "params": {}
        })

        if self.telegram:
            await self.telegram.send_alert(f"📞 I am answering a call from {caller} for you, Boss.")

        # 2. Sentient Interaction Loop
        # In a real setup, we would stream audio. For this protocol:
        # We use a short 'Human-like' delay before the first word.
        await asyncio.sleep(1.2)
        
        # 3. Use the Mirror Pipeline for the 'Greeting'
        greeting = await mirror_engine.process(f"Hello? This is {caller} calling.")
        logger.info(f"JARVIS Speaking on Call: {greeting}")
        
        # Route to TTS (Assuming local speaker or mobile stream)
        # For now, we simulate the logic flow
        
        self.is_on_call = False

# Instance
telephony_agent = TelephonyAgent()
