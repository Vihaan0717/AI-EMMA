import asyncio
import datetime
import json
import logging
import os
from pathlib import Path
from core.health_store import health_store
from core.logger import get_logger

logger = get_logger("HealthWatchdog")

# Path to check for morning wakeup signals
_WAKEUP_TIME_DEFAULT = "06:30"
_TIMEOUT_GRACE_MINUTES = 2
_ALERT_DELAY_MINUTES = 10

class HealthWatchdog:
    def __init__(self, bridge, brain=None):
        self.bridge = bridge
        self.brain = brain
        self.running = False
        
        self.target_wakeup = _WAKEUP_TIME_DEFAULT
        self.grace_period = datetime.timedelta(minutes=_TIMEOUT_GRACE_MINUTES)
        self.alert_delay = datetime.timedelta(minutes=_ALERT_DELAY_MINUTES)
        
        self.user_checked_in = False
        self.last_check_date = None

    async def start(self):
        self.running = True
        logger.info(f"HealthWatchdog started. Target morning wakeup check: {self.target_wakeup}")
        asyncio.create_task(self._routine_loop())
        asyncio.create_task(self._analysis_plan_cron())

    def stop(self):
        self.running = False

    def check_in(self):
        """Called whenever the owner sends a WhatsApp message."""
        self.user_checked_in = True
        logger.info("[Watchdog] User checked in. Morning alert suppressed for today.")

    async def _routine_loop(self):
        while self.running:
            try:
                now = datetime.datetime.now()
                current_date = now.date().isoformat()
                
                # Reset check-in status on a new day
                if current_date != self.last_check_date:
                    self.user_checked_in = False
                    self.last_check_date = current_date
                
                # Check if it is the target wakeup check time
                target_dt = datetime.datetime.strptime(f"{current_date} {self.target_wakeup}", "%Y-%m-%d %H:%M")
                
                # 1. First trigger: Target + 2 minutes grace (proactive good morning)
                check_start = target_dt + self.grace_period
                if now >= check_start and now < check_start + datetime.timedelta(minutes=1):
                    if not self.user_checked_in:
                        logger.info("[Watchdog] Wakeup window missed. Sending good morning message...")
                        
                        # Load mother style Good Morning check
                        msg = "Good Morning Kanna 😇💫"
                        try:
                            with open("config/mother_persona.json", "r", encoding="utf-8") as f:
                                config = json.load(f)
                                msg = config.get("daily_checks", ["Good Morning Kanna 😇💫"])[0]
                        except Exception:
                            pass
                        
                        admin_jid = os.getenv("ADMIN_NUMBER", "")
                        if admin_jid:
                            if "@" not in admin_jid: admin_jid = f"{admin_jid}@c.us"
                            await self.bridge._enqueue_outgoing(admin_jid, text=msg, media_path=None)
                
                # 2. Second trigger: Target + 12 minutes (scolding voice message)
                scold_start = target_dt + self.grace_period + self.alert_delay
                if now >= scold_start and now < scold_start + datetime.timedelta(minutes=1):
                    if not self.user_checked_in:
                        logger.warning("[Watchdog] Wakeup alert ignored. Sending scolding voice note...")
                        
                        # Generate scolding audio text in mother tone
                        scold_text = "Kanna, nidra lechava ledha? Amma ki chala benga ga undhi ra, okkasari message cheyyi!"
                        try:
                            with open("config/mother_persona.json", "r", encoding="utf-8") as f:
                                config = json.load(f)
                                scold_text = config.get("scolding_phrases", [scold_text])[0]
                        except Exception:
                            pass

                        # Render as voice note using bridge speaker
                        from services.voice_speaker import VoiceSpeaker
                        speaker = VoiceSpeaker()
                        ogg_path = await speaker.generate_voice_file(scold_text)
                        
                        admin_jid = os.getenv("ADMIN_NUMBER", "")
                        if admin_jid and ogg_path:
                            if "@" not in admin_jid: admin_jid = f"{admin_jid}@c.us"
                            # Enqueue voice note
                            await self.bridge._enqueue_outgoing(admin_jid, text=None, media_path=ogg_path)

            except Exception as e:
                logger.error(f"[Watchdog] Loop error: {e}")
            
            # Check routine every 30 seconds
            await asyncio.sleep(30)

    async def _analysis_plan_cron(self):
        """Runs nightly at 11:30 PM to compile health habits analysis using mother persona."""
        while self.running:
            try:
                now = datetime.datetime.now()
                # Run once a day at 23:30
                if now.hour == 23 and now.minute == 30:
                    today_str = now.date().isoformat()
                    log = health_store.get_log(today_str)
                    
                    meals = log.get("meals", [])
                    symptoms = log.get("symptoms", [])
                    
                    # Call AI to generate Mother's Analysis
                    prompt = f"""
                    Review the child's daily health logs:
                    Meals eaten today: {json.dumps(meals)}
                    Symptoms reported: {json.dumps(symptoms)}
                    
                    Generate a maternal health analysis and advice plan in Tenglish.
                    Act as their loving but concerned mother. Focus on regular eating habits, avoiding junk,
                    and sleeping early.
                    """
                    
                    mother_style = ""
                    try:
                        with open("config/mother_persona.json", "r", encoding="utf-8") as f:
                            config = json.load(f)
                            mother_style = config.get("tone_instructions", "")
                    except Exception:
                        pass
                        
                    from core.ai_engine import AIEngine
                    engine = AIEngine()
                    await engine.initialize()
                    analysis_plan = await engine.generate(prompt, system=mother_style)
                    await engine.close()
                    
                    log["analysis_plan"] = analysis_plan
                    health_store.save_log(log)
                    logger.info(f"[Watchdog] Successfully saved nightly health analysis plan for {today_str}")
                    
                    # Wait 60s to avoid double triggers in the same minute
                    await asyncio.sleep(60)
                    
            except Exception as e:
                logger.error(f"[Watchdog] Analysis cron error: {e}")
            
            await asyncio.sleep(15)
