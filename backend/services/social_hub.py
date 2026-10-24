import os
import sys
import asyncio
import logging
from typing import Dict, List, Any
# We will use playwright for personal account scraping.
# Ensure you run `playwright install` and login manually to save state.
from playwright.async_api import async_playwright, Page, BrowserContext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.agent_result import AgentResult

logger = logging.getLogger("jarvis.social_hub")

class SocialHub:
    """
    Manages connections to WhatsApp Web, Instagram, and Threads via Playwright.
    Since we are using personal accounts, we use a persistent browser context
    so you only have to log in (or scan QR) once.
    """
    def __init__(self, user_data_dir: str = "./social_browser_data"):
        self.user_data_dir = user_data_dir
        self.playwright = None
        self.browser = None
        self.context: BrowserContext = None
        self.ig_page: Page = None
        self.wa_page: Page = None
        self.threads_page: Page = None

    async def start(self):
        logger.info("[SocialHub] Starting browser automation for personal accounts...")
        self.playwright = await async_playwright().start()
        # Using a persistent context so session cookies and WhatsApp Web auth are saved
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=True, # Change to False if you need to scan a QR code or login!
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Initialize tabs
        self.wa_page = await self.context.new_page()
        self.ig_page = await self.context.new_page()
        
        # Navigate to platforms
        logger.info("[SocialHub] Connecting to WhatsApp Web...")
        await self.wa_page.goto("https://web.whatsapp.com/")
        
        logger.info("[SocialHub] Connecting to Instagram...")
        await self.ig_page.goto("https://www.instagram.com/direct/inbox/")
        
        logger.info("[SocialHub] Waiting for web apps to load...")
        await asyncio.sleep(5)
        
    async def get_unread_whatsapp_messages(self) -> List[Dict[str, str]]:
        """Scrapes unread messages from WhatsApp Web."""
        if not self.wa_page:
            return []
        
        # Wait for the unread badge selector (this is an example, WhatsApp Web DOM changes frequently)
        unread_elements = await self.wa_page.query_selector_all("span[aria-label*='unread message']")
        messages = []
        for el in unread_elements:
            # We would click the chat and read the latest messages here
            messages.append({"platform": "WhatsApp", "sender": "Unknown", "snippet": "New unread message detected."})
        return messages

    async def get_unread_instagram_messages(self) -> List[Dict[str, str]]:
        """Scrapes unread DMs from Instagram."""
        if not self.ig_page:
            return []
        
        # Checking for the unread dot in Instagram Direct Inbox
        unread_elements = await self.ig_page.query_selector_all("div[class*='x1lliihq'][class*='x1n2onr6']")
        messages = []
        for el in unread_elements:
             messages.append({"platform": "Instagram", "sender": "Unknown", "snippet": "New DM received."})
        return messages

    async def get_social_summary(self) -> str:
        """Aggregates all updates to respond to 'any updates on our social media?'."""
        wa_msgs = await self.get_unread_whatsapp_messages()
        ig_msgs = await self.get_unread_instagram_messages()
        
        total = len(wa_msgs) + len(ig_msgs)
        if total == 0:
            return AgentResult(
                status="success",
                confidence=1.0,
                sources=["WhatsApp", "Instagram"],
                answer="All quiet on the digital front, sir. No new messages on WhatsApp or Instagram.",
                needs_verification=False,
                errors=[]
            ).to_json()
            
        summary = f"You have {total} new updates. "
        if wa_msgs:
            summary += f"There are {len(wa_msgs)} new chats on WhatsApp. "
        if ig_msgs:
            summary += f"You have {len(ig_msgs)} new direct messages on Instagram. "
            
        return AgentResult(
            status="success",
            confidence=0.9,
            sources=["WhatsApp", "Instagram"],
            answer=summary,
            needs_verification=False,
            errors=[]
        ).to_json()

    async def read_social_messages(self, platform: str) -> str:
        """Reads detailed unread messages from a given platform."""
        platform = platform.lower()
        if platform == "whatsapp":
            return await self._read_whatsapp_details()
        elif platform == "instagram":
            return await self._read_instagram_details()
        else:
            return AgentResult(
                status="error",
                confidence=0.0,
                sources=[],
                answer="",
                needs_verification=False,
                errors=[f"Platform '{platform}' is not supported for reading yet."]
            ).to_json()

    async def _read_whatsapp_details(self) -> str:
        if not self.wa_page: 
            return AgentResult(
                status="error",
                confidence=0.0,
                sources=["WhatsApp"],
                answer="",
                needs_verification=True,
                errors=["WhatsApp not connected."]
            ).to_json()
        # Locate unread chat rows and grab the text from the preview snippet.
        unread_chats = await self.wa_page.query_selector_all("div[role='listitem']:has(span[aria-label*='unread message'])")
        if not unread_chats:
            return AgentResult(
                status="success",
                confidence=1.0,
                sources=["WhatsApp"],
                answer="There are no unread WhatsApp messages.",
                needs_verification=False,
                errors=[]
            ).to_json()
        
        details = []
        for chat in unread_chats:
            title_element = await chat.query_selector("span[title]")
            title = await title_element.get_attribute("title") if title_element else "Unknown Sender"
            text_content = await chat.inner_text()
            snippet = text_content.replace('\n', ' ').strip()
            details.append(f"From {title}: {snippet}")
        
        return AgentResult(
            status="success",
            confidence=0.8,
            sources=["WhatsApp"],
            answer="WhatsApp unread chats: " + " | ".join(details),
            needs_verification=False,
            errors=[]
        ).to_json()

    async def _read_instagram_details(self) -> str:
        if not self.ig_page: 
            return AgentResult(
                status="error",
                confidence=0.0,
                sources=["Instagram"],
                answer="",
                needs_verification=True,
                errors=["Instagram not connected."]
            ).to_json()
        # Instagram DM DOM is notoriously obscure; we approximate by reading the list item text
        unread_dms = await self.ig_page.query_selector_all("div[class*='x1lliihq'][class*='x1n2onr6']")
        if not unread_dms:
            return AgentResult(
                status="success",
                confidence=1.0,
                sources=["Instagram"],
                answer="There are no unread Instagram messages.",
                needs_verification=False,
                errors=[]
            ).to_json()
        
        return AgentResult(
            status="success",
            confidence=0.5,
            sources=["Instagram"],
            answer=f"You have {len(unread_dms)} unread Instagram threads. Note: Full content scraping requires clicking into each thread, which is currently in beta.",
            needs_verification=True,
            errors=[]
        ).to_json()

    async def close(self):
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

if __name__ == "__main__":
    async def test():
        hub = SocialHub()
        await hub.start()
        print(await hub.get_social_summary())
        await hub.close()
    
    asyncio.run(test())
