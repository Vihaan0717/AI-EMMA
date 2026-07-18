"""
Job Orchestrator - The main brain of CELO-APPLY.
Ties together: LinkedIn search → JD scrape → Resume tailor → Apply → Track → Notify.
Called by nexus_master.py via the job_hunt tool.
"""
import asyncio
import logging
from playwright.async_api import async_playwright

from backend.services.job_agent.linkedin_agent import (
    search_linkedin_jobs, scrape_job_description, easy_apply_linkedin
)
from backend.services.job_agent.resume_agent import tailor_resume, generate_cover_note
from backend.services.job_agent.job_tracker import (
    log_application, update_status, get_all_applications, format_applications_table
)
from backend.services.job_agent.whatsapp_notifier import (
    notify_application_sent, notify_status_change, notify_hunt_summary
)
from backend.services.job_agent.gmail_monitor import scan_gmail_for_job_replies

logger = logging.getLogger("jarvis.job_orchestrator")

LINKEDIN_BROWSER_DATA = "./social_browser_data"


async def _run_job_hunt(keywords: str, router, max_apply: int = 5) -> str:
    """
    Main async orchestration loop:
    1. Search LinkedIn for jobs
    2. For each job: scrape JD → tailor resume → Easy Apply → track → notify
    3. Return a summary string.
    """
    logger.info(f"[JobOrchestrator] Starting job hunt for: '{keywords}'")
    applied_jobs = []
    failed_jobs = []

    # Step 1: Search for jobs
    jobs = await search_linkedin_jobs(keywords, location="India", max_jobs=max_apply + 5)
    if not jobs:
        return f"[CELO-APPLY] No LinkedIn jobs found for '{keywords}'. LinkedIn session may need re-login."

    logger.info(f"[JobOrchestrator] Found {len(jobs)} jobs. Processing top {max_apply}...")

    # Step 2: Open one persistent context for all applications to save resources
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=LINKEDIN_BROWSER_DATA,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ],
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()

        for job in jobs[:max_apply]:
            title = job["title"]
            company = job["company"]
            url = job["url"]
            site = job.get("site", "LinkedIn")

            logger.info(f"[JobOrchestrator] Processing: {title} @ {company}")

            try:
                # Scrape full JD
                jd_text = await scrape_job_description(url) if url else ""

                # Tailor resume + cover note using LLM
                tailored = tailor_resume(title, company, jd_text, router)
                cover = generate_cover_note(title, company, jd_text, router)

                # Attempt Easy Apply
                success = await easy_apply_linkedin(page, url, tailored, cover)

                if success:
                    job_id = log_application(title, company, site, url, f"Auto-applied via JARVIS")
                    applied_jobs.append({"title": title, "company": company, "id": job_id})
                    notify_application_sent(title, company, site, job_id)
                    logger.info(f"[JobOrchestrator] ✅ Applied to {title} @ {company} | ID: #{job_id}")
                else:
                    failed_jobs.append({"title": title, "company": company})
                    logger.warning(f"[JobOrchestrator] ❌ Failed to apply to {title} @ {company}")

            except Exception as e:
                logger.error(f"[JobOrchestrator] Error processing {title}: {e}")
                failed_jobs.append({"title": title, "company": company, "error": str(e)})
                continue

        await context.close()

    # Step 3: Send summary notification
    if applied_jobs:
        notify_hunt_summary(len(applied_jobs), applied_jobs)

    # Build result string for JARVIS to read aloud
    result = f"[CELO-APPLY] Job Hunt Complete.\n"
    result += f"✅ Successfully applied to {len(applied_jobs)} jobs.\n"
    result += f"❌ Failed/skipped: {len(failed_jobs)} jobs.\n\n"
    if applied_jobs:
        result += "Applied to:\n" + "\n".join([f"  • {j['title']} @ {j['company']} (ID #{j['id']})" for j in applied_jobs])
    if failed_jobs:
        result += "\n\nFailed:\n" + "\n".join([f"  • {j['title']} @ {j['company']}" for j in failed_jobs])
    result += "\n\nWhatsApp notification sent to +91 9154716156."
    return result


async def _check_gmail_updates(router) -> str:
    """Scan Gmail for job reply emails and update tracker + notify."""
    apps = get_all_applications()
    if not apps:
        return "[CELO-APPLY] No tracked applications found. Run job_hunt first."

    logger.info("[JobOrchestrator] Scanning Gmail for job replies...")
    updates = await scan_gmail_for_job_replies(apps)

    if not updates:
        return "[CELO-APPLY] No new job-related emails found in Gmail."

    results = []
    for u in updates:
        if u.get("job_id"):
            update_status(u["job_id"], u["new_status"])
            notify_status_change(u["title"], u["company"], u["new_status"], u["job_id"])
            results.append(f"  • {u['title']} @ {u['company']} → {u['new_status']} (Email: '{u['subject']}')")
        else:
            results.append(f"  • Unmatched email from {u['sender']}: '{u['subject']}' → {u['new_status']}")

    return "[CELO-APPLY] Gmail Scan Complete.\n" + "\n".join(results)


def run_job_hunt(keywords: str, router, max_apply: int = 5) -> str:
    """Sync wrapper for nexus_master to call."""
    return asyncio.run(_run_job_hunt(keywords, router, max_apply))


def run_gmail_check(router) -> str:
    """Sync wrapper for nexus_master to call."""
    return asyncio.run(_check_gmail_updates(router))
