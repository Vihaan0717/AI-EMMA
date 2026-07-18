import logging
import asyncio
import os
from datetime import datetime
try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired
except ImportError:
    Client = None

logger = logging.getLogger("Nexus.InstagramMonitor")

class InstagramMonitor:
    """
    Service to monitor Instagram notifications and direct messages.
    Uses instagrapi to poll for new unread threads and routes them to JARVIS.
    """
    def __init__(self, bus=None):
        self.bus = bus
        self.running = False
        self.unread_count = 0
        self.notifications = []
        self.client = None
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
        self.session_file = "config/ig_session.json"
        
        # Keep track of message IDs we've already processed
        self.processed_message_ids = set()

    async def start(self):
        if not Client:
            logger.error("[Instagram] instagrapi not installed. Run 'pip install instagrapi'")
            return

        if not self.username or not self.password:
            logger.warning("[Instagram] Credentials not found in .env (IG_USERNAME/IG_PASSWORD). Polling disabled.")
            return

        self.running = True
        logger.info("[Instagram] Monitoring service started.")
        
        asyncio.create_task(self._init_and_poll())

    def _handle_challenge(self, username, choice):
        """
        Automatically handles Instagram login challenge.
        Instagrapi pauses and calls this synchronously.
        """
        logger.warning(f"[Instagram] Challenge requested for {username}. Method: {choice}")
        if choice == 1:
            logger.info("[Instagram] Attempting to extract code from Gmail automatically...")
            return self._get_code_from_email()
        return False

    def _get_code_from_email(self) -> str:
        """Connects to IMAP to fetch 6-digit verification code from Instagram."""
        import imaplib
        import email
        import re
        import time
        
        email_user = os.getenv("IG_EMAIL")
        email_pass = os.getenv("IG_EMAIL_PASSWORD")
        
        if not email_user or not email_pass:
            logger.error("[Instagram] Cannot automate verification: IG_EMAIL/IG_EMAIL_PASSWORD not set in .env")
            return False

        # Wait a few seconds for the email to arrive
        time.sleep(10)
        
        try:
            logger.info(f"[Instagram] Connecting to IMAP for {email_user}...")
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email_user, email_pass)
            mail.select("inbox")

            # Search for emails from Instagram
            result, data = mail.search(None, '(FROM "security@mail.instagram.com" UNSEEN)')
            
            if result == 'OK' and data[0]:
                email_ids = data[0].split()
                if not email_ids:
                    return False
                    
                latest_email_id = email_ids[-1]
                result, msg_data = mail.fetch(latest_email_id, '(RFC822)')
                
                if result == 'OK':
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    # Find 6-digit code
                    match = re.search(r'\b(\d{6})\b', body)
                    if match:
                        code = match.group(1)
                        logger.info(f"[Instagram] Found verification code: {code}")
                        return code
            logger.error("[Instagram] Verification code not found in inbox.")
            return False
        except Exception as e:
            logger.error(f"[Instagram] Email extraction failed: {e}")
            return False

    async def _init_and_poll(self):
        try:
            self.client = Client()
            
            # --- AUTOMATIC VERIFICATION HANDLER ---
            self.client.challenge_code_handler = self._handle_challenge
            
            # Try to login using session file first to avoid 2FA/blocks
            if os.path.exists(self.session_file):
                logger.info("[Instagram] Loading session from file...")
                # Run sync functions in executor
                await asyncio.to_thread(self.client.load_settings, self.session_file)
                try:
                    await asyncio.to_thread(self.client.login, self.username, self.password)
                    logger.info("[Instagram] Logged in successfully via session.")
                except LoginRequired:
                    logger.info("[Instagram] Session expired. Re-logging in...")
                    await asyncio.to_thread(self.client.login, self.username, self.password)
                    await asyncio.to_thread(self.client.dump_settings, self.session_file)
            else:
                logger.info("[Instagram] No session file found. Logging in...")
                await asyncio.to_thread(self.client.login, self.username, self.password)
                await asyncio.to_thread(self.client.dump_settings, self.session_file)
                
            logger.info("[Instagram] Successfully authenticated. Beginning polling loops.")
            asyncio.create_task(self._poll_instagram())
            await self._poll_feed_reels_and_likes()
        except Exception as e:
            logger.error(f"[Instagram] Failed to initialize: {e}")
            self.running = False

    async def _poll_feed_reels_and_likes(self):
        """Polls user feed, reels, and likes every 30 minutes to extract trends and patterns."""
        while self.running:
            try:
                logger.info("[Instagram Feed] Scanning timeline, reels, and likes for trend analysis...")
                
                # Fetch recent liked media (up to 15 items)
                liked_medias = await asyncio.to_thread(self.client.user_liked_medias, amount=15)
                # Fetch timeline feed (reels & feed from followed accounts, up to 15 items)
                feed_items = await asyncio.to_thread(self.client.feed_timeline, amount=15)
                
                self._save_media_insights(liked_medias, feed_items)
            except Exception as e:
                logger.error(f"[Instagram Feed] Polling error: {e}")
                
            # Scan every 30 minutes (1800 seconds) to avoid rate limits
            await asyncio.sleep(1800)

    def _save_media_insights(self, liked_medias, feed_items):
        """Extracts captions, hashtags, and likes, and dumps them to memory/social_insights.json."""
        import json
        insights_path = "memory/social_insights.json"
        
        data = {
            "last_updated": datetime.now().isoformat(),
            "liked_items": [],
            "feed_items": []
        }
        
        # Parse liked items
        for m in liked_medias:
            data["liked_items"].append({
                "id": m.id,
                "caption": m.caption_text,
                "media_type": m.media_type,
                "product_type": m.product_type, # 'clips' for Reels, 'feed' for posts
                "user": m.user.username if m.user else "unknown",
                "like_count": m.like_count
            })
            
        # Parse feed items
        for m in feed_items:
            data["feed_items"].append({
                "id": m.id,
                "caption": m.caption_text,
                "media_type": m.media_type,
                "product_type": m.product_type,
                "user": m.user.username if m.user else "unknown",
                "like_count": m.like_count
            })
            
        try:
            os.makedirs(os.path.dirname(insights_path), exist_ok=True)
            with open(insights_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logger.info(f"[Instagram Feed] Successfully updated social insights database: {insights_path}")
        except Exception as e:
            logger.error(f"[Instagram Feed] Failed to save social insights: {e}")

    async def _poll_instagram(self):
        """Polls Instagram Direct Messages."""
        while self.running:
            try:
                # Fetch unread threads
                threads = await asyncio.to_thread(self.client.direct_threads, amount=10, selected_filter="unread")
                
                for thread in threads:
                    if thread.last_permanent_item:
                        msg = thread.last_permanent_item
                        msg_id = msg.id
                        
                        # Check if it's a new message
                        if msg_id not in self.processed_message_ids and str(msg.user_id) != str(self.client.user_id):
                            self.processed_message_ids.add(msg_id)
                            self.unread_count += 1
                            
                            sender_name = thread.users[0].username if thread.users else str(msg.user_id)
                            text = msg.text
                            
                            logger.info(f"[Instagram] New DM from {sender_name}: {text}")
                            
                            self.notifications.append({
                                "thread_id": thread.id,
                                "sender": sender_name,
                                "text": text,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            # Push to message bus if configured
                            if self.bus:
                                await self.bus.publish("user_message", {
                                    "platform": "instagram",
                                    "thread_id": thread.id,
                                    "sender": sender_name,
                                    "text": text,
                                    "timestamp": datetime.now().isoformat()
                                })
                                
            except Exception as e:
                logger.error(f"[Instagram] Polling error: {e}")
                
            # Poll every 60 seconds to avoid API limits
            await asyncio.sleep(60)

    async def send_message(self, thread_id: str, text: str):
        """Send a direct message reply."""
        if not self.client:
            logger.error("[Instagram] Cannot send message: Client not initialized.")
            return False
            
        try:
            logger.info(f"[Instagram] Sending reply to thread {thread_id}...")
            await asyncio.to_thread(self.client.direct_send, text, thread_ids=[thread_id])
            return True
        except Exception as e:
            logger.error(f"[Instagram] Failed to send message: {e}")
            return False

    def get_notification_summary(self):
        """Returns a summary of unread items."""
        return {
            "count": self.unread_count,
            "latest": self.notifications[-3:] if self.notifications else []
        }

    async def add_mock_notification(self, sender: str, text: str):
        """Utility for testing."""
        self.unread_count += 1
        self.notifications.append({
            "sender": sender,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"[Instagram] New notification from {sender}")
