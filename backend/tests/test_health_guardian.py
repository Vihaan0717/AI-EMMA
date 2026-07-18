import unittest
import os
import sys
import datetime
import json
import shutil
from pathlib import Path

# Ensure project root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.health_store import health_store
from agents.vision_agent import VisionTracker

class TestHealthGuardian(unittest.TestCase):
    """
    Test suite for checking health logs database,
    mother persona config retrieval, VLM meal photo processing,
    and command routing logic.
    """

    def setUp(self):
        self.today = datetime.date.today().isoformat()
        # Clean current day's log if exists for isolation
        log = health_store.get_log(self.today)
        log["meals"] = []
        log["symptoms"] = []
        log["mood"] = "neutral"
        log["analysis_plan"] = ""
        health_store.save_log(log)

    def test_health_store_logging(self):
        """Verify adding meals and symptoms to SQLite logs operates correctly."""
        # Add meal
        meal = {
            "time": "08:30 AM",
            "items": ["Apple", "Milk"],
            "portion_sizes": "1 cup",
            "macros": {"calories": 150, "protein": 8, "carbs": 25, "fats": 2}
        }
        health_store.add_meal(self.today, meal)
        
        # Add symptom
        health_store.add_symptom(self.today, "Stomach pain")

        # Recover log and assert
        log = health_store.get_log(self.today)
        self.assertEqual(len(log["meals"]), 1)
        self.assertEqual(log["meals"][0]["items"], ["Apple", "Milk"])
        self.assertIn("Stomach pain", log["symptoms"])

    def test_mother_persona_loading(self):
        """Verify mother profile config is valid and readable."""
        config_path = Path("config/mother_persona.json")
        self.assertTrue(config_path.exists())
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            self.assertIn("language", config)
            self.assertIn("tone_instructions", config)
            self.assertIn("scolding_phrases", config)

    def test_vision_meal_fallback(self):
        """Test Vision Tracker's analyze_meal method handling and fallback gracefully."""
        tracker = VisionTracker()
        # Call with dummy/non-existent path to trigger VLM fallback cleanly
        res = getattr(self, "async_run", lambda coroutine: asyncio.run(coroutine))(
            tracker.analyze_meal("non_existent_image.jpg")
        )
        self.assertIn("items", res)
        self.assertIn("macros", res)

    def test_watchdog_check_in(self):
        """Verify checking in with the routine watchdog updates status correctly."""
        from core.health_watchdog import HealthWatchdog
        # Create watchdog instance
        watchdog = HealthWatchdog(None)
        self.assertFalse(watchdog.user_checked_in)
        watchdog.check_in()
        self.assertTrue(watchdog.user_checked_in)

    @staticmethod
    def async_run(coro):
        import asyncio
        return asyncio.run(coro)

if __name__ == "__main__":
    unittest.main()
