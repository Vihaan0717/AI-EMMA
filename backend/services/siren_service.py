import winsound
import time
import logging

logger = logging.getLogger("SirenService")

class SirenService:
    """
    100% Free Emergency Alarm Service.
    Uses the PC's built-in speakers to alert the Boss.
    """
    def __init__(self):
        self.active = False

    def play_siren(self, duration_seconds: int = 5):
        """Plays a loud police-like siren through the PC speakers."""
        logger.warning(f"🚨 SIREN TRIGGERED for {duration_seconds} seconds!")
        self.active = True
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration_seconds:
                # Police Siren Effect (High-Low)
                for freq in range(500, 1500, 50): # Ramp up
                    winsound.Beep(freq, 20)
                for freq in range(1500, 500, -50): # Ramp down
                    winsound.Beep(freq, 20)
        except Exception as e:
            logger.error(f"Siren failed: {e}")
        finally:
            self.active = False
            logger.info("Siren stopped.")

if __name__ == "__main__":
    # Test the Siren directly
    siren = SirenService()
    print("\nWARNING: Playing Siren Test in 2 seconds! Turn down your volume if needed.")
    time.sleep(2)
    siren.play_siren(3)
