import os
import time
import logging
import asyncio
import threading
from collections import deque
import mss
import pygetwindow as gw

logger = logging.getLogger("ScreenMonitor")

class ScreenMonitor:
    """
    Passively monitors the user's screen and active window.
    Keeps a rolling buffer of screenshots and tracks window context.
    """
    def __init__(self, buffer_size=3, interval=5):
        self.buffer_size = buffer_size
        self.interval = interval
        self.running = False
        self.thread = None
        
        self.active_window_title = "Unknown"
        self.screenshot_buffer = deque(maxlen=self.buffer_size)
        
        self.tmp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp", "vision_buffer")
        os.makedirs(self.tmp_dir, exist_ok=True)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info(f"ScreenMonitor started. Capturing every {self.interval}s.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("ScreenMonitor stopped.")

    def get_latest_context(self):
        """Returns the active window title and the latest screenshot path."""
        latest_screenshot = self.screenshot_buffer[-1] if self.screenshot_buffer else None
        return {
            "active_window": self.active_window_title,
            "latest_screenshot": latest_screenshot
        }

    def _monitor_loop(self):
        with mss.mss() as sct:
            # We assume primary monitor is index 1 in mss
            monitor = sct.monitors[1]
            
            while self.running:
                try:
                    # 1. Capture Active Window
                    try:
                        active_win = gw.getActiveWindow()
                        if active_win and active_win.title:
                            self.active_window_title = active_win.title
                    except Exception as e:
                        # Some platforms/environments might throw errors
                        pass

                    # 2. Capture Screen
                    timestamp = int(time.time())
                    filename = os.path.join(self.tmp_dir, f"screen_{timestamp}.png")
                    
                    sct_img = sct.grab(monitor)
                    mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
                    
                    self.screenshot_buffer.append(filename)
                    
                    # 3. Cleanup old files from disk
                    self._cleanup_old_files()

                except Exception as e:
                    logger.error(f"Screen capture failed: {e}")

                time.sleep(self.interval)

    def _cleanup_old_files(self):
        """Delete files in tmp_dir that are not in the current buffer."""
        try:
            for f in os.listdir(self.tmp_dir):
                filepath = os.path.join(self.tmp_dir, f)
                if filepath not in self.screenshot_buffer:
                    os.remove(filepath)
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sm = ScreenMonitor(interval=2)
    sm.start()
    try:
        time.sleep(10)
        print("Latest Context:", sm.get_latest_context())
    finally:
        sm.stop()
