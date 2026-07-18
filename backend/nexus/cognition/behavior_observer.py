import time
import logging
import sqlite3
import os
import asyncio
from typing import Dict, List

logger = logging.getLogger("nexus.behavior")

class BehaviorObserver:
    """
    NEXUS-X Behavioral & Intent Analyst.
    Tracks app usage, screen content, and dwell time to build a Personal Twin model.
    """
    def __init__(self, brain=None, db_path="memory/behavior_habits.db"):
        self.brain = brain
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self.current_app = None
        self.start_time = time.time()
        
        self.last_known_context = {}
        self._proactive_task = None

    async def start_proactive_loop(self):
        """Starts the background cron loop to evaluate context periodically."""
        if not self._proactive_task:
            self._proactive_task = asyncio.create_task(self._proactive_tick())
            logger.info("[Behavior] Proactive context loop started.")

    async def _proactive_tick(self):
        while True:
            try:
                await asyncio.sleep(300) # Check every 5 minutes
                await self._evaluate_context_proactively()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[Behavior] Proactive tick error: {e}")

    async def _evaluate_context_proactively(self):
        """Evaluates stored context to trigger JARVIS to initiate a conversation."""
        if not self.last_known_context:
            return
            
        activity = self.last_known_context.get("activity")
        
        # Example: If the user has been driving for a while
        if activity == "driving":
            logger.info("[Behavior] User is driving. Sending proactive check-in.")
            # We can use the Telegram service to push a proactive notification
            if self.brain and 'telegram' in self.brain.modules:
                telegram = self.brain.modules['telegram']
                if telegram:
                    await telegram.send_message(
                        self.brain.privacy.get_admin(), 
                        "Sir, I see you are currently driving. Would you like me to read your unread emails or play some music?"
                    )


    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS habits
                     (id INTEGER PRIMARY KEY, app_package TEXT, category TEXT, 
                      dwell_time INTEGER, interest_score INTEGER, timestamp DATETIME)''')
        conn.commit()
        conn.close()

    async def process_screen_event(self, app_package: str, extracted_text: str):
        """Processes a screen update from the Flutter accessibility service."""
        now = time.time()
        
        # Calculate dwell time for the previous app
        if self.current_app and self.current_app != app_package:
            dwell_time = int(now - self.start_time)
            await self._analyze_and_store(self.current_app, dwell_time)
            self.start_time = now
            
        self.current_app = app_package
        
        # Analyze current screen text for interests
        await self._detect_interests(extracted_text, app_package)

    async def _detect_interests(self, text: str, app: str):
        """Classifies content and updates interest profiles."""
        interests = {
            "Coding": ["python", "flutter", "dart", "java", "github", "stack overflow"],
            "Aquariums": ["shrimp", "aquarium", "tank", "aquascape", "betta"],
            "Hyderabad": ["charminar", "biryani", "hitech city", "telangana"],
            "Gaming": ["steam", "discord", "fps", "rpg", "tuf a15"]
        }
        
        found = []
        for category, keywords in interests.items():
            if any(k in text.lower() for k in keywords):
                found.append(category)
                logger.info(f"[Behavior] Detected Interest: {category} in {app}")
                # Emit event for real-time adaptation
                if hasattr(self, 'bus') and self.bus:
                    self.bus.publish("BEHAVIOR", {"type": "INTEREST_DETECTED", "category": category, "app": app})
        
        # Content Pattern: Sequential Interest
        if len(found) > 1:
            logger.info(f"[Behavior] Multimodal Content Pattern: {found}")
            
        # PROACTIVE: Detect Potential Telugu Slang for Scholar Agent
        if self.brain and self.brain.scholar:
            words = text.split()
            for word in words:
                if len(word) > 3 and any(ord(c) > 127 for c in word): # Simple non-ascii check
                     logger.info(f"[Behavior] Proactive Slang Detection: {word}")
                     asyncio.create_task(self.brain.scholar.classify_term(word, "screen_discovery"))
            
        return found

    async def _analyze_and_store(self, app: str, dwell_time: int):
        """Stores app usage habits."""
        # Interest score: longer dwell = higher score
        score = 1 if dwell_time < 60 else 5
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO habits (app_package, category, dwell_time, interest_score, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (app, "General", dwell_time, score, time.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        logger.info(f"[Behavior] Logged {app} for {dwell_time}s (Score: {score})")

    def get_adb_usage_stats(self):
        """Extracts deep diagnostic data via ADB (Free Extraction)."""
        import subprocess
        try:
            # Requires ADB to be installed and phone connected
            cmd = "adb shell dumpsys usagestats --checkin"
            output = subprocess.check_output(cmd, shell=True).decode()
            return output
        except Exception as e:
            logger.warning(f"ADB Extraction failed: {e}")
            return None

    async def process_mobile_context(self, context_data: Dict):
        """Processes continuous telemetry from the mobile companion app."""
        client_id = context_data.get("client_id", "unknown")
        gps = context_data.get("gps")
        activity = context_data.get("activity")
        battery = context_data.get("battery")
        
        self.last_known_context = context_data
        
        # Log to DB or memory
        logger.info(f"[Behavior] Mobile Context Update - Activity: {activity}, Batt: {battery}%")
        
        # Example proactive trigger: if battery is low, warn the user
        if battery and isinstance(battery, (int, float)) and battery <= 15:
            if hasattr(self, 'bus') and self.bus:
                self.bus.publish("SYSTEM_ALERT", {
                    "urgency": "high",
                    "message": "Sir, your phone battery is critically low.",
                    "target": client_id
                })
        
        # Future: Store GPS trail for location-based proactive suggestions

