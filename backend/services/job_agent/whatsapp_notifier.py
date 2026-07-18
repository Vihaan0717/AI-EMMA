"""
WhatsApp Notifier - Sends job alerts to Rohit via WhatsApp Web using Playwright.
Phone: +91 9154716156
Uses persistent browser context so session is already logged in.
"""
import asyncio
import logging
import urllib.parse
from playwright.async_api import async_playwright

logger = logging.getLogger("jarvis.whatsapp_notifier")

WHATSAPP_PHONE = "919154716156"  # E.164 without the '+'
SOCIAL_BROWSER_DATA = "./social_browser_data"


async def send_whatsapp_message(message: str) -> bool:
    """
    Sends a WhatsApp message to Rohit's number using the wa.me deep link method.
    Uses the persistent browser session so no re-login needed.
    Returns True on success.
    """
    encoded_msg = urllib.parse.quote(message)
    wa_url = f"https://web.whatsapp.com/send?phone={WHATSAPP_PHONE}&text={encoded_msg}"

    logger.info(f"[WhatsAppNotifier] Sending message to +{WHATSAPP_PHONE}...")
    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=SOCIAL_BROWSER_DATA,
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            page = await context.new_page()
            await page.goto(wa_url)

            # Wait for the send button to appear (WhatsApp Web loads dynamically)
            send_btn_selector = 'button[aria-label="Send"]'
            try:
                await page.wait_for_selector(send_btn_selector, timeout=30000)
                await page.click(send_btn_selector)
                await asyncio.sleep(2)
                logger.info("[WhatsAppNotifier] ✅ Message sent successfully.")
                await context.close()
                return True
            except Exception as e:
                logger.error(f"[WhatsAppNotifier] Failed to find send button: {e}")
                await context.close()
                return False
    except Exception as e:
        logger.error(f"[WhatsAppNotifier] Browser error: {e}")
        return False


def notify_application_sent(job_title: str, company: str, site: str, job_id: int):
    """Notify Rohit that an application was successfully submitted."""
    msg = (
        f"🚀 *[JARVIS - Job Hunt]*\n"
        f"✅ *Applied!*\n"
        f"📌 *Role:* {job_title}\n"
        f"🏢 *Company:* {company}\n"
        f"🌐 *Platform:* {site}\n"
        f"🆔 *Tracking ID:* #{job_id}\n"
        f"📅 Status: _Pending Review_"
    )
    asyncio.run(send_whatsapp_message(msg))


def notify_status_change(job_title: str, company: str, new_status: str, job_id: int):
    """Notify Rohit of a status update from Gmail scan."""
    emoji_map = {
        "interview_invite": "🎯",
        "offer": "🎉",
        "rejection": "❌",
        "assessment": "📝",
        "pending": "⏳",
    }
    emoji = emoji_map.get(new_status, "📬")
    msg = (
        f"{emoji} *[JARVIS - Job Update]*\n"
        f"*Role:* {job_title} @ {company}\n"
        f"*New Status:* {new_status.replace('_', ' ').title()}\n"
        f"🆔 Tracking ID: #{job_id}"
    )
    asyncio.run(send_whatsapp_message(msg))


def notify_hunt_summary(total_applied: int, jobs: list):
    """Send a summary message at the end of a job hunt session."""
    job_lines = "\n".join([f"  • {j['title']} @ {j['company']}" for j in jobs[:10]])
    msg = (
        f"📊 *[JARVIS - Hunt Complete]*\n"
        f"I applied to *{total_applied}* jobs this session.\n\n"
        f"*Recent Applications:*\n{job_lines}\n\n"
        f"_Type 'job status' to see the full tracker._"
    )
    asyncio.run(send_whatsapp_message(msg))
