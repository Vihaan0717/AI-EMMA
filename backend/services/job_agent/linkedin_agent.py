"""
LinkedIn Agent - Pure Playwright automation for job search and Easy Apply.
Mimics human behavior: random delays, mouse movements, typing speed variation.
Uses persistent browser context (social_browser_data) so login is preserved.
"""
import asyncio
import logging
import random
import os
from playwright.async_api import async_playwright, Page, BrowserContext

logger = logging.getLogger("jarvis.linkedin_agent")

LINKEDIN_BROWSER_DATA = "./social_browser_data"
LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs/search/"
RESUME_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "MugasalaRohitResume.pdf")
RESUME_ABS_PATH = os.path.abspath(RESUME_PATH)

# --- Human-mimicry helpers ---

async def _human_delay(min_ms=400, max_ms=1600):
    await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

async def _human_type(page: Page, selector: str, text: str):
    """Type text character by character with random delays to mimic humans."""
    await page.click(selector)
    await page.fill(selector, "")
    for char in text:
        await page.type(selector, char, delay=random.randint(40, 140))
        await asyncio.sleep(random.uniform(0, 0.05))

async def _random_scroll(page: Page):
    """Randomly scroll up/down to mimic reading the page."""
    scroll_amount = random.randint(200, 800)
    direction = random.choice([1, -1])
    await page.mouse.wheel(0, scroll_amount * direction)
    await _human_delay(300, 900)


# --- Core Agent Functions ---

async def search_linkedin_jobs(keywords: str, location: str = "India", max_jobs: int = 10) -> list:
    """
    Search LinkedIn for jobs matching keywords.
    Returns a list of dicts: {title, company, url, description_snippet}
    """
    logger.info(f"[LinkedInAgent] Searching LinkedIn for: '{keywords}' in {location}")
    jobs = []

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
        page: Page = await context.new_page()

        try:
            # Navigate directly to the search URL to avoid flaky input selectors
            import urllib.parse
            encoded_kw = urllib.parse.quote(keywords)
            encoded_loc = urllib.parse.quote(location)
            # f_AL=true forces LinkedIn to only show 'Easy Apply' jobs!
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_kw}&location={encoded_loc}&f_AL=true"
            
            await page.goto(search_url)
            await _human_delay(3000, 5000)

            # Check if logged in
            if "authwall" in page.url or "login" in page.url or "checkpoint" in page.url:
                logger.warning("[LinkedInAgent] Authwall or CAPTCHA detected. Please run LINKEDIN_LOGIN.bat manually to authenticate.")
                await context.close()
                return []

            # Filter for Easy Apply is handled by URL parameter f_AL=true

            # Wait for jobs to load
            card_selector = ".job-card-container, .jobs-search-results__list-item, .job-search-card, li[data-occludable-job-id]"
            try:
                await page.wait_for_selector(card_selector, timeout=10000)
            except Exception:
                pass

            # Scrape job listings
            job_cards = await page.query_selector_all(card_selector)
            logger.info(f"[LinkedInAgent] Found {len(job_cards)} job cards.")

            for card in job_cards[:max_jobs]:
                try:
                    title_el = await card.query_selector(".job-card-list__title, .base-search-card__title, h3, a.job-card-container__link")
                    company_el = await card.query_selector(".artdeco-entity-lockup__subtitle, .job-card-container__primary-description, .base-search-card__subtitle, .job-card-container__company-name, h4")
                    link_el = await card.query_selector("a.job-card-list__title, a.base-card__full-link, a.job-card-container__link, a")

                    title = (await title_el.inner_text()).strip() if title_el else "Unknown"
                    company = (await company_el.inner_text()).strip() if company_el else "Unknown"
                    href = await link_el.get_attribute("href") if link_el else ""
                    url = f"https://www.linkedin.com{href}" if href and href.startswith("/") else href
                    
                    # Deduplicate by removing query parameters from url
                    base_url = url.split("?")[0]
                    if any(j["url"].split("?")[0] == base_url for j in jobs):
                        continue

                    jobs.append({
                        "title": title,
                        "company": company,
                        "url": url,
                        "site": "LinkedIn",
                        "description_snippet": "",
                    })
                except Exception as card_err:
                    logger.warning(f"[LinkedInAgent] Error parsing job card: {card_err}")
                    continue

        except Exception as e:
            logger.error(f"[LinkedInAgent] Search error: {e}")
        finally:
            await context.close()

    return jobs


async def scrape_job_description(job_url: str) -> str:
    """Open a job listing page and extract the full job description text."""
    logger.info(f"[LinkedInAgent] Scraping JD from: {job_url}")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=LINKEDIN_BROWSER_DATA,
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ],
        )
        page = await context.new_page()
        try:
            await page.goto(job_url)
            await _human_delay(2000, 4000)
            await _random_scroll(page)

            # Try to click "See more" to expand description
            see_more = await page.query_selector('button[aria-label="Click to see more description"]')
            if see_more:
                await see_more.click()
                await _human_delay(600, 1200)

            desc_el = await page.query_selector(".jobs-description__content")
            if desc_el:
                text = await desc_el.inner_text()
                await context.close()
                return text.strip()
        except Exception as e:
            logger.error(f"[LinkedInAgent] Failed to scrape JD: {e}")
        finally:
            await context.close()
    return ""


async def easy_apply_linkedin(page: Page, job_url: str, tailored_summary: str, cover_note: str) -> bool:
    """
    Attempt LinkedIn Easy Apply on a job page.
    Fills in form fields, uploads resume, and submits.
    Returns True if application was submitted.
    """
    logger.info(f"[LinkedInAgent] Starting Easy Apply for: {job_url}")

    # Navigate to the job
    await page.goto(job_url)
    await _human_delay(2000, 4000)
    await _random_scroll(page)

    # Click Easy Apply button
    try:
        easy_apply = await page.wait_for_selector(
            'button[aria-label*="Easy Apply"], .jobs-apply-button--top-card button, button.jobs-apply-button', timeout=10000
        )
        await easy_apply.click()
        await _human_delay(1500, 2500)
    except Exception:
        logger.warning("[LinkedInAgent] No Easy Apply button found on this job.")
        return False

    # Handle multi-step modal
    max_steps = 8
    for step in range(max_steps):
        await _human_delay(1000, 2000)
        logger.info(f"[LinkedInAgent] Easy Apply step {step + 1}...")

        # Handle resume upload
        upload_input = await page.query_selector('input[type="file"]')
        if upload_input:
            logger.info("[LinkedInAgent] Uploading resume...")
            await upload_input.set_input_files(RESUME_ABS_PATH)
            await _human_delay(1000, 2000)

        # Handle text areas (cover letter / additional info)
        textareas = await page.query_selector_all("textarea")
        for ta in textareas:
            placeholder = (await ta.get_attribute("placeholder") or "").lower()
            if "cover" in placeholder or "summary" in placeholder or "tell us" in placeholder:
                await ta.fill(cover_note)
                await _human_delay(500, 1000)
            elif "additional" in placeholder or "anything else" in placeholder:
                await ta.fill(tailored_summary)
                await _human_delay(500, 1000)

        # Fill in text inputs (phone, etc.)
        text_inputs = await page.query_selector_all('input[type="text"]:visible, input[type="tel"]:visible')
        for inp in text_inputs:
            label = (await inp.get_attribute("aria-label") or "").lower()
            if "phone" in label or "mobile" in label:
                val = await inp.input_value()
                if not val:
                    await _human_type(page, f'[aria-label="{await inp.get_attribute("aria-label")}"]', "9154716156")
                    await _human_delay(300, 700)

        # Handle Radio Buttons (Default to "Yes" or first option)
        try:
            unselected_radios = await page.query_selector_all('input[type="radio"]:not(:checked)')
            for radio in unselected_radios:
                label_text = await page.evaluate('(r) => r.labels && r.labels.length > 0 ? r.labels[0].innerText : ""', radio)
                if label_text and "Yes" in label_text:
                    await radio.click(force=True)
                    await _human_delay(300, 500)
        except Exception:
            pass

        # Handle Select Dropdowns (Select first valid option)
        try:
            selects = await page.query_selector_all('select')
            for select in selects:
                val = await page.evaluate('(s) => s.value', select)
                if not val or val == 'Select an option':
                    await page.evaluate('(s) => { if(s.options.length > 1) { s.selectedIndex = 1; s.dispatchEvent(new Event("change", { bubbles: true })); } }', select)
                    await _human_delay(300, 500)
        except Exception:
            pass

        # Check for "Next" or "Review" or "Submit" button
        next_btn = await page.query_selector('button[aria-label="Continue to next step"]')
        review_btn = await page.query_selector('button[aria-label="Review your application"]')
        submit_btn = await page.query_selector('button[aria-label="Submit application"]')

        if submit_btn:
            logger.info("[LinkedInAgent] Found Submit button. Submitting application!")
            await submit_btn.click()
            await _human_delay(2000, 3000)
            return True
        elif review_btn:
            await review_btn.click()
        elif next_btn:
            await next_btn.click()
        else:
            # Try to find any forward button
            fwd_btn = await page.query_selector('button:has-text("Next"), button:has-text("Continue"), button:has-text("Submit")')
            if fwd_btn:
                await fwd_btn.click()
            else:
                logger.warning(f"[LinkedInAgent] Could not find navigation button at step {step + 1}.")
                break

    logger.warning("[LinkedInAgent] Max steps reached without successful submission.")
    return False
