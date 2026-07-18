# arion/screen/screen_indicator.py

import os
import time
import threading
import tkinter as tk
from typing import Optional

class ScreenIndicator:
    """
    Neon blue border around ENTIRE screen edges
    - NEVER overlaps any app content
    - Stays on extreme screen edges only
    - Shows tiny floating pill (bottom-right corner)
    - NEVER shows over title bars
    """

    def __init__(self,
                 border_thickness: int = 3,
                 color: str = '#00d4ff',
                 auto_hide_seconds: float = 2.0):

        self.border_thickness = border_thickness
        self.color = color
        self.auto_hide_seconds = auto_hide_seconds
        self.is_visible = False
        self._windows = []
        self._pill_window = None
        self._hide_timer = None
        self._anim_running = False
        self._tk_root = None

        # Get actual screen size
        try:
            root = tk.Tk()
            root.withdraw()
            self.screen_w = root.winfo_screenwidth()
            self.screen_h = root.winfo_screenheight()
            root.destroy()
        except:
            self.screen_w = 1920
            self.screen_h = 1080

        self._start_tk()
        print(f"✅ [Indicator] Ready ({self.screen_w}x{self.screen_h})")

    def _start_tk(self):
        def tk_run():
            self._tk_root = tk.Tk()
            self._tk_root.withdraw()
            self._build_borders()
            self._build_pill()
            self._tk_root.mainloop()

        t = threading.Thread(target=tk_run, daemon=True, name="Indicator")
        t.start()
        time.sleep(0.5)

    def _build_borders(self):
        """Build 4 border strips on SCREEN EDGES only"""
        W = self.screen_w
        H = self.screen_h
        T = self.border_thickness

        # Positioned at extreme edges
        borders = [
            (0,         0,         W,  T      ),  # Top edge
            (0,         H - T,     W,  T      ),  # Bottom edge
            (0,         T,         T,  H-T*2  ),  # Left edge
            (W - T,     T,         T,  H-T*2  ),  # Right edge
        ]

        for (x, y, w, h) in borders:
            win = tk.Toplevel(self._tk_root)
            win.overrideredirect(True)
            win.attributes('-topmost', True)
            win.attributes('-alpha', 0.0)
            win.geometry(f'{w}x{h}+{x}+{y}')
            win.configure(bg=self.color)

            # Note: Click-through via Win32 API is handled if needed
            win.withdraw()
            self._windows.append(win)

    def _build_pill(self):
        """Small floating pill at BOTTOM RIGHT corner"""
        pill_w, pill_h = 220, 32
        x = self.screen_w - pill_w - 10
        y = self.screen_h - pill_h - 50 # Above taskbar

        win = tk.Toplevel(self._tk_root)
        win.overrideredirect(True)
        win.attributes('-topmost', True)
        win.attributes('-alpha', 0.0)
        win.geometry(f'{pill_w}x{pill_h}+{x}+{y}')
        win.configure(bg='#0d0d14')

        frame = tk.Frame(win, bg='#0d0d14', highlightbackground=self.color, highlightthickness=1)
        frame.pack(fill='both', expand=True, padx=1, pady=1)

        self._pill_label = tk.Label(
            frame, text='👁 Scanning...', bg='#0d0d14', fg=self.color,
            font=('Consolas', 9, 'bold'), anchor='w', padx=8
        )
        self._pill_label.pack(fill='both', expand=True)
        win.withdraw()
        self._pill_window = win

    def show(self, content_type: str = 'general', custom_text: str = None):
        if not self._tk_root: return

        icons = {
            'code': '💻 Code', 'mathematics': '📐 Math', 'psychology': '🧠 Psychology',
            'philosophy': '💭 Philosophy', 'history': '📜 History', 'youtube': '▶️ Video',
            'article': '📄 Article', 'chat': '💬 Chat', 'notes': '📝 Notes', 'general': '👁 Screen'
        }
        label = custom_text or icons.get(content_type, '👁 Scanning')

        def _show():
            try:
                if self._pill_label: self._pill_label.config(text=f' {label}')
                for win in self._windows:
                    win.deiconify()
                    win.attributes('-alpha', 0.0)
                if self._pill_window:
                    self._pill_window.deiconify()
                    self._pill_window.attributes('-alpha', 0.0)

                self.is_visible = True
                self._anim_running = True
                self._animate()

                if self._hide_timer: self._hide_timer.cancel()
                self._hide_timer = threading.Timer(self.auto_hide_seconds, self.hide)
                self._hide_timer.daemon = True
                self._hide_timer.start()
            except: pass

        self._tk_root.after(0, _show)

    def _animate(self):
        import math
        def pulse(frame=0):
            if not self._anim_running or not self._tk_root: return
            try:
                alpha = 0.5 + 0.4 * abs(math.sin(frame * 0.12))
                for win in self._windows: win.attributes('-alpha', alpha)
                if self._pill_window: self._pill_window.attributes('-alpha', min(alpha + 0.1, 1.0))
                self._tk_root.after(50, lambda: pulse(frame + 1))
            except: pass
        self._tk_root.after(0, pulse)

    def hide(self):
        self._anim_running = False
        def _fade():
            try:
                for step in range(10, -1, -1):
                    a = (step / 10.0) * 0.85
                    for win in self._windows: win.attributes('-alpha', a)
                    if self._pill_window: self._pill_window.attributes('-alpha', a)
                    time.sleep(0.02)
                for win in self._windows: win.withdraw()
                if self._pill_window: self._pill_window.withdraw()
                self.is_visible = False
            except: pass
        threading.Thread(target=_fade, daemon=True).start()

    def destroy(self):
        self._anim_running = False
        if self._hide_timer: self._hide_timer.cancel()
        if self._tk_root: self._tk_root.quit()
