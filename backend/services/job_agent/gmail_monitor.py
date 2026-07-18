"""
Gmail Monitor - Pure Playwright headless browser automation.
Logs into Gmail, reads job application reply emails, classifies them,
updates the job tracker, and fires WhatsApp notifications.
NO API KEYS USED. Mimics human browsing behavior.
"""
import asyncio
import logging
import random
import re
from playwright.async_api import async_playwright, Page

logger = logging.getLogger("jarvis.gmail_monitor")

GMAIL_BROWSER_DATA = "./social_browser_data"  # Shared persistent context

# Keywords to classify email subjects
EMAIL_CLASSIFIERS = {
    "interview_invite": [
        "interview", "schedule a call", "we would like to meet",
        "shortlisted", "next round", "speaking with you"
    ],
    "offer": [
        "offer letter", "job offer", "congratulations", "we are pleased to offer",
        "employment offer"
    ],
    "assessment": [
        "assessment", "test", "coding challenge", "assignment", "hackerrank",
        "online test", "technical round"
    ],
    "rejected": [
        "unfortunately", "not moving forward", "not selected", "other candidates",
        "not be proceeding", "regret to inform", "unsuccessful"
    ],
}

JOB_SITE_DOMAINS = [
    "linkedin", "naukri", "indeed", "glassdoor", "internshala",
    "monster", "shine", "foundit", "recruitment", "hiring", "hr@", "talent"
]


async def _human_delay(min_ms=500, max_ms=1800):
    await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


def _classify_email(subject: str, snippet: str) -> str:
    """Classify an email based on subject + snippet keywords."""
    combined = (subject + " " + snippet).lower()
    for status, keywords in EMAIL_CLASSIFIERS.items():
        for kw in keywords:
            if kw in combined:
                return status
    return "pending"


def _is_job_related(sender: str, subject: str) -> bool:
    """Check if an email is job-application related."""
    combined = (sender + " " + subject).lower()
    return any(domain in combined for domain in JOB_SITE_DOMAINS)


async def scan_gmail_for_job_replies(tracker_apps: list) -> list:
    """
    Opens Gmail in Playwright, reads the inbox, finds job-related emails,
    and returns a list of dicts: {job_id, title, company, new_status, subject}
    """
    updates = []
    logger.info("[GmailMonitor] Launching Gmail in headless browser...")

    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=GMAIL_BROWSER_DATA,
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                viewport={"width": 1280, "height": 900},
            )
            page: Page = await context.new_page()
            await page.goto("https://mail.google.com/mail/u/0/#inbox")
            await _human_delay(3000, 5000)

            # Check if we're logged in
            if "accounts.google.com" in page.url:
                logger.warning("[GmailMonitor] Gmail not logged in in this browser session. Please log in manually once.")
                await context.close()
                return []

            logger.info("[GmailMonitor] Gmail loaded. Scanning inbox rows...")
            await page.wait_for_selector("tr.zA", timeout=15000)

            # Read all email rows in the inbox
            email_rows = await page.query_selector_all("tr.zA")
            logger.info(f"[GmailMonitor] Found {len(email_rows)} emails in inbox.")

            for row in email_rows[:30]:  # Scan top 30 emails
                try:
                    sender_el = await row.query_selector("span.zM")
                    subject_el = await row.query_selector("span.bog")
                    snippet_el = await row.query_selector("span.y2")

                    sender = await sender_el.inner_text() if sender_el else ""
                    subject = await subject_el.inner_text() if subject_el else ""
                    snippet = await snippet_el.inner_text() if snippet_el else ""

                    if not _is_job_related(sender, subject):
                        continue

                    new_status = _classify_email(subject, snippet)
                    logger.info(f"[GmailMonitor] Job email: '{subject}' | Status: {new_status}")

                    # Try to match to a tracked application by company/title name
                    matched_app = None
                    for app in tracker_apps:
                        company_lower = app["company"].lower()
                        title_lower = app["title"].lower()
                        combined_email = (sender + subject + snippet).lower()
                        if company_lower in combined_email or any(w in combined_email for w in title_lower.split()):
                            matched_app = app
                            break

                    updates.append({
                        "job_id": matched_app["id"] if matched_app else None,
                        "title": matched_app["title"] if matched_app else "Unknown",
                        "company": matched_app["company"] if matched_app else sender,
                        "new_status": new_status,
                        "subject": subject,
                        "sender": sender,
                    })

                    await _human_delay(200, 600)

                except Exception as row_err:
                    logger.warning(f"[GmailMonitor] Error reading email row: {row_err}")
                    continue

            await context.close()

    except Exception as e:
        logger.error(f"[GmailMonitor] Error scanning Gmail: {e}")

    return updates
