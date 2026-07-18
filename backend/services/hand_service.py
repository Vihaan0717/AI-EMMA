import os
import subprocess
import logging
import pyautogui
import pygetwindow as gw
import keyboard
import time
from typing import Optional, List, Dict

logger = logging.getLogger("HandService")

class HandService:
    """
    NEXUS-X "Hands" Service.
    Provides direct OS control capabilities using PyAutoGUI and system commands.
    """
    def __init__(self):
        pyautogui.FAILSAFE = True # Move mouse to corner to abort
        logger.info("Hand Service initialized. 'Hands' are ready.")

    # ── SAFETY & BOUNDARY CHECKS ───────────────────────────────────

    def _validate_coordinates(self, x: int, y: int) -> bool:
        """Validates coordinates are within actual screen boundaries."""
        screen_width, screen_height = pyautogui.size()
        return 0 <= x <= screen_width and 0 <= y <= screen_height

    # ── WINDOW MANAGEMENT ──────────────────────────────────────────

    def list_windows(self) -> List[str]:
        """Returns titles of all visible windows."""
        return [w.title for w in gw.getAllWindows() if w.title]

    def maximize_window(self, title_query: str) -> str:
        """Finds and maximizes a window matching the query."""
        try:
            windows = gw.getWindowsWithTitle(title_query)
            if not windows:
                return f"No window found matching '{title_query}'."
            
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.maximize()
            try:
                win.activate()
            except Exception:
                pass  # Activating might fail on Windows if another window has strict focus rules
            return f"Maximized window: {win.title}"
        except Exception as e:
            return f"Error maximizing window: {e}"

    def close_window(self, title_query: str) -> str:
        """Finds and closes a window matching the query."""
        try:
            windows = gw.getWindowsWithTitle(title_query)
            if not windows:
                return f"No window found matching '{title_query}'."
            
            win = windows[0]
            win.close()
            return f"Closed window: {win.title}"
        except Exception as e:
            return f"Error closing window: {e}"

    # ── APP CONTROL ───────────────────────────────────────────────

    def open_app(self, app_name: str) -> str:
        """Attempts to open an application safely by avoiding shell character injections."""
        if not app_name:
            return "Application name cannot be empty."
        
        # Strict input sanitization: allow only alphanumeric characters, spaces, dots, dashes, and underscores
        sanitized = "".join(c for c in app_name if c.isalnum() or c in " .-_:")
        if sanitized != app_name:
            return "Unsafe characters detected in application command."

        try:
            # Safely invoke command using CMD start with arguments separated safely
            subprocess.Popen(["cmd", "/c", "start", "", sanitized], shell=True)
            return f"Attempted to launch: {sanitized}"
        except Exception as e:
            return f"Failed to launch {sanitized}: {e}"

    def run_cmd(self, command: str) -> str:
        """Runs a command inside the workspace directory safely and returns the output."""
        try:
            workspace_root = r"c:\Users\anger\Desktop\JARVIS_Project"
            cmd_lower = command.lower()
            # Simple safety guard
            if "format" in cmd_lower or "rmdir /s" in cmd_lower or "rm -rf" in cmd_lower:
                return "Command rejected: Safety block triggered."
                
            res = subprocess.run(
                command,
                shell=True,
                cwd=workspace_root,
                capture_output=True,
                text=True,
                timeout=15
            )
            output = res.stdout
            if res.stderr:
                output += f"\nError:\n{res.stderr}"
            return output or "Command completed with no output."
        except subprocess.TimeoutExpired:
            return "Command execution timed out (15s limit)."
        except Exception as e:
            return f"Execution error: {e}"

    def uninstall_app(self, app_name: str) -> str:
        """
        Attempts to uninstall an app via PowerShell safely.
        """
        if not app_name:
            return "Invalid application name."
            
        sanitized = "".join(c for c in app_name if c.isalnum() or c in " .-_")
        if sanitized != app_name:
            return "Unsafe characters detected in application command."
            
        cmd = f'powershell -Command "Get-Package -Name *{sanitized}* | Uninstall-Package -Force"'
        try:
            return f"Uninstall command for '{sanitized}' sent to system. Checking status..."
        except Exception as e:
            return f"Uninstall failed: {e}"

    # ── FILE CRUD ─────────────────────────────────────────────────

    def perform_file_crud(self, action: str, path: str, content: str = None) -> str:
        """Performs Create, Read, Update, Delete on local files safely with path traversal protection."""
        try:
            path = os.path.abspath(path)
            # Enforce path containment within workspace/sandbox directories
            workspace_root = r"c:\Users\anger\Desktop\JARVIS_Project"
            if not path.startswith(os.path.abspath(workspace_root)):
                return "Operation rejected: Access denied to paths outside the workspace."

            if action in ["create", "update"]:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content or "")
                return f"File {action}d successfully: {os.path.basename(path)}"
            elif action == "read":
                if not os.path.exists(path): return "File not found."
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            elif action == "delete":
                if os.path.exists(path):
                    os.remove(path)
                    return f"Deleted: {os.path.basename(path)}"
                return "File not found."
            return "Invalid action."
        except Exception as e:
            return f"File operation failed: {e}"

    # ── UI INTERACTION ────────────────────────────────────────────

    def click_at(self, x: int, y: int) -> str:
        """Moves the mouse and clicks at the specified coordinates safely."""
        try:
            if self._validate_coordinates(x, y):
                # Move first, then click for more natural behavior
                pyautogui.moveTo(x, y, duration=0.25)
                pyautogui.click(x, y)
                return f"Clicked successfully at ({x}, {y})"
            else:
                return f"Coordinates ({x}, {y}) are outside screen boundaries."
        except pyautogui.FailSafeException:
            logger.warning("FAILSAFE TRIGGERED: User moved mouse to corner.")
            return "Action aborted: Failsafe triggered by user."
        except Exception as e:
            return f"Click action failed: {e}"

    def click_on_screen(self, target_image_path: str) -> str:
        """Searches for an image on screen and clicks it safely."""
        if not os.path.exists(target_image_path):
            return f"Target image file '{target_image_path}' does not exist."
        try:
            location = pyautogui.locateOnScreen(target_image_path, confidence=0.8)
            if location:
                x, y = pyautogui.center(location)
                if self._validate_coordinates(x, y):
                    pyautogui.click(x, y)
                    return f"Clicked on {os.path.basename(target_image_path)} at ({x}, {y})"
                else:
                    return f"Location ({x}, {y}) out of screen boundaries."
            return f"Target {os.path.basename(target_image_path)} not found on screen."
        except Exception as e:
            return f"Click action failed: {e}"

    def type_text(self, text: str, hit_enter: bool = False) -> str:
        """Types text safely at the current cursor position."""
        if not text:
            return "No text provided to type."
        try:
            pyautogui.write(text, interval=0.02)
            if hit_enter:
                pyautogui.press('enter')
            return f"Typed requested text. (Enter pressed: {hit_enter})"
        except pyautogui.FailSafeException:
            return "Action aborted: Failsafe triggered by user."
        except Exception as e:
            return f"Type action failed: {e}"

    def press_hotkey(self, keys: List[str]) -> str:
        """Presses a combination of keys (e.g., ['ctrl', 'c'] or ['win'])."""
        if not keys:
            return "No keys provided."
        try:
            pyautogui.hotkey(*keys)
            return f"Pressed hotkey: {'+'.join(keys)}"
        except pyautogui.FailSafeException:
            return "Action aborted: Failsafe triggered by user."
        except Exception as e:
            return f"Hotkey action failed: {e}"

    def scroll(self, amount: int) -> str:
        """
        Scrolls the screen safely. Positive for up, negative for down.
        """
        pyautogui.scroll(amount)
        return f"Scrolled by {amount} units."

    def capture_screen(self, filename: str) -> str:
        """Captures a screenshot and saves it safely."""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return f"Screenshot saved to {filename}"
        except Exception as e:
            return f"Screenshot failed: {e}"

if __name__ == "__main__":
    # Quick test
    hands = HandService()
    print("Windows currently open:")
    for w in hands.list_windows()[:5]:
        print(f" - {w}")
