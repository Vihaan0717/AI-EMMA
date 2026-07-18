# arion/screen/screen_watcher.py

import os
import time
import threading
import base64
import io
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Dict
import mss
from PIL import Image
import pytesseract
import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = os.getenv(
    'TESSERACT_PATH',
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'
)

class ScreenWatcher:
    """
    Background monitor for screen content.
    Integrated with Neon Indicator.
    """

    def __init__(self,
                 capture_interval: int = 15,
                 on_content_detected: Callable = None,
                 save_screenshots: bool = False,
                 show_indicator: bool = True):

        self.capture_interval = capture_interval
        self.on_content_detected = on_content_detected
        self.save_screenshots = save_screenshots
        self.show_indicator_enabled = show_indicator
        self.is_running = False
        self.last_text = ""
        self.capture_count = 0

        # Screenshot save path
        if save_screenshots:
            self.screenshot_dir = Path('arion/screen/screenshots')
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Neon Indicator
        self.indicator = None
        if show_indicator and os.getenv('SCREEN_INDICATOR', 'true').lower() == 'true':
            try:
                # Add project root to path for local imports if needed
                import sys
                from arion.screen.screen_indicator import ScreenIndicator
                self.indicator = ScreenIndicator(
                    border_thickness=4,
                    color='#00d4ff',
                    auto_hide_seconds=2.5
                )
                print("[Watcher] Neon indicator active")
            except Exception as e:
                print(f"[Watcher] Indicator not available: {e}")

        print("Screen Watcher initialized")

    def capture_screen(self, monitor: int = 1) -> Optional[Image.Image]:
        """Capture current screen area"""
        try:
            with mss.mss() as sct:
                mon = sct.monitors[monitor]
                screenshot = sct.grab(mon)
                img = Image.frombytes(
                    'RGB',
                    screenshot.size,
                    screenshot.bgra,
                    'raw', 'BGRX'
                )
                return img
        except Exception:
            return None

    def extract_text(self, image: Image.Image) -> str:
        """Extract text via OCR (English + Telugu)"""
        try:
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            # Resize for better OCR accuracy
            scaled = cv2.resize(thresh, None, fx=1.5, fy=1.5)
            text = pytesseract.image_to_string(
                scaled, lang='eng+tel',
                config='--psm 3 --oem 3'
            )
            return text.strip()
        except Exception:
            return ""

    def detect_content_type(self, text: str) -> str:
        """Categorize screen content based on keywords"""
        t = text.lower()
        checks = [
            ('code',        ['def ', 'class ', 'import ', 'const ', 'function', 'return', 'npm', 'node', 'python', '#!/']),
            ('mathematics', ['formula', 'equation', 'theorem', 'solve', 'calculate', '∫', '∑', 'π', '=']),
            ('psychology',  ['psychology', 'behavior', 'cognitive', 'emotion', 'mental', 'therapy', 'brain']),
            ('philosophy',  ['philosophy', 'ethics', 'consciousness', 'aristotle', 'plato', 'nietzsche']),
            ('history',     ['century', 'ancient', 'historical', 'empire', 'dynasty', 'war']),
            ('youtube',     ['youtube', 'subscribe', 'views', 'channel', 'like', 'comment']),
            ('article',     ['author', 'published', 'introduction', 'conclusion', 'paragraph']),
            ('chat',        ['whatsapp', 'message', 'delivered', 'typing', 'online', 'seen']),
            ('notes',       ['obsidian', '[[', ']]', '- [ ]', 'backlink']),
        ]
        for content_type, keywords in checks:
            if any(k in t for k in keywords):
                return content_type
        return 'general'

    def has_changed(self, new_text: str, threshold: float = 0.3) -> bool:
        """Check if screen content changed significantly (Jaccard similarity)"""
        if not self.last_text: return True
        if not new_text: return False
        old_w = set(self.last_text.lower().split())
        new_w = set(new_text.lower().split())
        if not old_w and not new_w: return False
        overlap = old_w & new_w
        union = old_w | new_w
        similarity = len(overlap) / len(union) if union else 1.0
        return (1.0 - similarity) > threshold

    def image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL image to B64 for GPT-Vision"""
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def take_snapshot(self) -> Dict:
        """Manual snapshot trigger"""
        if self.indicator:
            self.indicator.show('general', 'Taking Snapshot...')
        
        image = self.capture_screen()
        if not image: return {'error': 'Capture failed'}

        text = self.extract_text(image)
        content_type = self.detect_content_type(text)

        if self.indicator:
            self.indicator.show(content_type)

        return {
            'text': text,
            'content_type': content_type,
            'image_b64': self.image_to_base64(image),
            'timestamp': datetime.now().isoformat(),
            'word_count': len(text.split())
        }

    def start_watching(self, monitor: int = 1):
        """Start background watch loop"""
        self.is_running = True
        print(f"Starting screen watch (every {self.capture_interval}s)...")

        def watch_loop():
            while self.is_running:
                try:
                    if self.indicator:
                        self.indicator.show('general', 'Scanning...')

                    image = self.capture_screen(monitor)
                    if image is None:
                        time.sleep(self.capture_interval)
                        continue

                    text = self.extract_text(image)

                    if text and self.has_changed(text):
                        content_type = self.detect_content_type(text)
                        
                        if self.indicator:
                            self.indicator.show(content_type)

                        self.capture_count += 1
                        
                        if self.save_screenshots:
                            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                            path = self.screenshot_dir / f"{ts}_{content_type}.png"
                            image.save(path)

                        if self.on_content_detected:
                            self.on_content_detected({
                                'text': text,
                                'content_type': content_type,
                                'image_b64': self.image_to_base64(image),
                                'timestamp': datetime.now().isoformat()
                            })

                        self.last_text = text

                    time.sleep(self.capture_interval)

                except Exception as e:
                    print(f"[Watcher] Loop Error: {e}")
                    time.sleep(self.capture_interval)

        self.watch_thread = threading.Thread(target=watch_loop, daemon=True, name="ScreenWatcherThread")
        self.watch_thread.start()
        print("Screen watching started in background!")

    def stop_watching(self):
        """Halt background monitoring"""
        self.is_running = False
        if self.indicator:
            self.indicator.hide()
        print("Screen watching stopped")
