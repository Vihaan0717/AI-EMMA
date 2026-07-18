import os
import logging
import ctypes
import ctypes.wintypes
from typing import List, Dict, Optional, Any

logger = logging.getLogger("DOMEService")

# Setup Windows API calls via ctypes
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

class DOMEService:
    """
    DOME (Desktop Object Model Engine) Service.
    Enables structural querying of Windows desktop windows, control trees, and geometry
    for deterministic UI element mapping without brittle coordinates.
    """

    def __init__(self):
        logger.info("DOME Service successfully loaded. DOM Engine is online.")

    def get_window_hierarchy(self) -> List[Dict[str, Any]]:
        """
        Retrieves all top-level window structures on the desktop including handles,
        titles, class names, and layout geometry.
        """
        windows = []

        def enum_windows_callback(hwnd, lParam):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                title = ""
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buffer, length + 1)
                    title = buffer.value

                # Get class name
                class_buffer = ctypes.create_unicode_buffer(256)
                user32.GetClassNameW(hwnd, class_buffer, 256)
                class_name = class_buffer.value

                # Get coordinates
                rect = ctypes.wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))
                
                windows.append({
                    "hwnd": hwnd,
                    "title": title,
                    "class": class_name,
                    "rect": {
                        "left": rect.left,
                        "top": rect.top,
                        "right": rect.right,
                        "bottom": rect.bottom,
                        "width": rect.right - rect.left,
                        "height": rect.bottom - rect.top
                    }
                })
            return True

        # Run window enumeration
        user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
        return windows

    def find_element_by_title(self, query: str) -> Optional[Dict[str, Any]]:
        """Finds the first visible window or child control matching the given title query."""
        # 1. Search top-level windows first
        top_level_windows = self.get_window_hierarchy()
        for win in top_level_windows:
            if win["title"] and query.lower() in win["title"].lower():
                return win
        
        # 2. Search child controls of visible top-level windows
        for win in top_level_windows:
            if win["rect"]["width"] > 50 and win["rect"]["height"] > 50:
                try:
                    controls = self.query_control_tree(win["hwnd"])
                    for ctrl in controls:
                        if ctrl["title"] and query.lower() in ctrl["title"].lower():
                            return ctrl
                except Exception as e:
                    logger.debug(f"Failed to query child controls for hwnd {win['hwnd']}: {e}")
        return None


    def query_control_tree(self, parent_hwnd: int) -> List[Dict[str, Any]]:
        """
        Enumerates child controls within a parent window handle (hwnd).
        Builds a lightweight object tree for targeted automation inputs.
        """
        controls = []

        def enum_child_callback(hwnd, lParam):
            class_buffer = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buffer, 256)
            class_name = class_buffer.value

            length = user32.GetWindowTextLengthW(hwnd)
            title = ""
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                title = buffer.value

            rect = ctypes.wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))

            controls.append({
                "hwnd": hwnd,
                "class": class_name,
                "title": title,
                "rect": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                    "width": rect.right - rect.left,
                    "height": rect.bottom - rect.top
                }
            })
            return True

        user32.EnumChildWindows(parent_hwnd, WNDENUMPROC(enum_child_callback), 0)
        return controls

if __name__ == "__main__":
    dome = DOMEService()
    print("Found active top-level windows:")
    for w in dome.get_window_hierarchy()[:5]:
        print(f" - [{w['hwnd']}] {w['title']} (Class: {w['class']})")
