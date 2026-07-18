"""
NEXUS-X Browser Agent
=====================
Wraps Playwright to allow agentic control over a web browser.
Enables navigation, clicking, form filling, and scraping.
Used for real-world interactions (e.g., finding food, reading live sites).
"""

import logging
import asyncio
from typing import Optional, Dict

logger = logging.getLogger("BrowserAgent")

class BrowserAgent:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def initialize(self):
        """Initializes the headless browser."""
        if self.playwright:
            return
            
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            logger.info("BrowserAgent initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize BrowserAgent: {e}")
            self.playwright = None

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            self.browser = None
            self.page = None

    async def browse(self, url: str) -> str:
        """Navigates to a URL and returns a summary of the page."""
        await self.initialize()
        if not self.page:
            return "Error: Browser not initialized."
            
        try:
            await self.page.goto(url, wait_until="networkidle")
            title = await self.page.title()
            
            # Get a clean version of the text
            text = await self.page.evaluate("document.body.innerText")
            preview = text[:1500] + ("..." if len(text) > 1500 else "")
            
            return f"Navigated to '{title}' ({url}).\nPreview:\n{preview}"
        except Exception as e:
            return f"Browse error: {e}"

    async def click(self, selector: str) -> str:
        """Clicks an element matching the CSS selector."""
        await self.initialize()
        if not self.page:
            return "Error: Browser not initialized."
            
        try:
            await self.page.click(selector)
            await self.page.wait_for_timeout(1000) # Wait for page reaction
            return f"Successfully clicked '{selector}'."
        except Exception as e:
            return f"Click error: {e}"

    async def fill_form(self, selector: str, value: str) -> str:
        """Fills an input field matching the CSS selector."""
        await self.initialize()
        if not self.page:
            return "Error: Browser not initialized."
            
        try:
            await self.page.fill(selector, value)
            return f"Filled '{selector}' with '{value}'."
        except Exception as e:
            return f"Fill error: {e}"

# Global singleton
browser_agent = BrowserAgent()
