import os
import time
import logging
from typing import Optional
from mcp_base.agent_mcp_server import AgentMCPServer

try:
    import pyautogui
    from PIL import ImageGrab
    # Safety feature: Moving mouse to any of the 4 corners of the screen raises pyautogui.FailSafeException
    pyautogui.FAILSAFE = True 
    # Add a slight delay to all pyautogui actions to look more human and prevent freezing
    pyautogui.PAUSE = 0.5 
except ImportError:
    logging.warning("pyautogui or Pillow not installed. Vision MCP will fail to execute tools.")

vision_server = AgentMCPServer("vision_mcp", "Computer Vision and UI Controller")
mcp = vision_server.mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Temporary directory for screenshots
SCREENSHOT_DIR = os.path.join(os.getcwd(), "vision", "captures")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot(filename: str = "latest_capture.png") -> str:
    """
    Takes a full screenshot of the primary monitor and saves it to disk.
    Returns the absolute file path of the image for Vision LLM analysis.
    """
    try:
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        # Take screenshot
        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        logger.info(f"Screenshot saved to {filepath}")
        return f"Screenshot successfully captured and saved at: {filepath}"
    except Exception as e:
        return f"Failed to take screenshot: {str(e)}"

def click_coordinates(x: int, y: int, clicks: int = 1, button: str = "left") -> str:
    """
    Physically moves the mouse to the exact X and Y coordinates and clicks.
    WARNING: If you lose control, move your physical mouse to any corner of the screen to trigger the FailSafe.
    """
    try:
        # Move the mouse slowly to the location (duration=0.5s makes it look human and gives user time to react)
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click(clicks=clicks, button=button)
        return f"Successfully moved mouse and clicked at ({x}, {y}) using {button} button."
    except pyautogui.FailSafeException:
        logger.warning("FAILSAFE TRIGGERED BY USER")
        return "Execution aborted: User triggered the physical mouse FailSafe by moving cursor to the corner."
    except Exception as e:
        return f"Failed to click coordinates: {str(e)}"

def type_text(text: str, press_enter: bool = False) -> str:
    """
    Simulates human typing on the keyboard.
    """
    try:
        # Type text with a tiny interval to simulate real typing
        pyautogui.write(text, interval=0.05)
        if press_enter:
            pyautogui.press('enter')
        return f"Successfully typed: '{text}'"
    except pyautogui.FailSafeException:
        return "Execution aborted: User triggered the physical mouse FailSafe."
    except Exception as e:
        return f"Failed to type text: {str(e)}"

def press_key(key: str) -> str:
    """
    Simulates pressing a specific key (e.g., 'enter', 'tab', 'esc', 'win').
    """
    try:
        pyautogui.press(key)
        return f"Successfully pressed key: '{key}'"
    except Exception as e:
        return f"Failed to press key: {str(e)}"

if mcp:
    mcp.tool()(take_screenshot)
    mcp.tool()(click_coordinates)
    mcp.tool()(type_text)
    mcp.tool()(press_key)

if __name__ == "__main__":
    logger.info("Starting Vision MCP Server...")
    vision_server.run()
