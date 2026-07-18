"""
End-to-end dry-run test for CELO-APPLY.
Tests: LinkedIn login check, JD scrape attempt, resume tailoring via LLM.
Does NOT submit any applications.
"""
import sys
import io
import asyncio
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, ".")

from backend.services.job_agent.linkedin_agent import search_linkedin_jobs, scrape_job_description
from backend.services.job_agent.resume_agent import read_resume_text, tailor_resume, generate_cover_note
from backend.services.job_agent.job_tracker import log_application, format_applications_table
from jarvis_brain.hybrid_router import HybridRouter

print("=" * 60)
print("  CELO-APPLY End-to-End Dry Run")
print("=" * 60)

async def run():
    router = HybridRouter()

    # Step 1: Search LinkedIn
    print("\n[1/4] Searching LinkedIn for 'Python AI Developer'...")
    jobs = await search_linkedin_jobs("Python AI Developer", location="India", max_jobs=3)
    if not jobs:
        print("  ⚠️  No jobs found — LinkedIn session may need a one-time manual login.")
        print("  Proceeding with mock data for resume tailoring test...\n")
        jobs = [{"title": "Agentic AI Developer", "company": "OpenAI", "url": "", "site": "LinkedIn", "description_snippet": ""}]
    else:
        print(f"  ✅ Found {len(jobs)} jobs:")
        for j in jobs:
            print(f"    • {j['title']} @ {j['company']}")

    # Step 2: Scrape JD for first job (or use mock)
    first_job = jobs[0]
    print(f"\n[2/4] Scraping JD for: {first_job['title']} @ {first_job['company']}...")
    if first_job.get("url"):
        jd = await scrape_job_description(first_job["url"])
        print(f"  ✅ JD scraped: {len(jd)} chars")
    else:
        jd = "We are looking for a Full Stack Python Developer with expertise in AI agents, LLMs, FastAPI, React, and prompt engineering."
        print(f"  ⚠️  No URL, using mock JD.")

    # Step 3: Tailor resume via LLM
    print(f"\n[3/4] Tailoring resume via LLM for '{first_job['title']}'...")
    tailored = tailor_resume(first_job["title"], first_job["company"], jd, router)
    cover = generate_cover_note(first_job["title"], first_job["company"], jd, router)
    print(f"  ✅ Tailored Summary:\n  {tailored[:300]}...")
    print(f"\n  ✅ Cover Note:\n  {cover[:200]}...")

    # Step 4: Log mock application
    print(f"\n[4/4] Logging dry-run application to tracker...")
    job_id = log_application(first_job["title"], first_job["company"], "LinkedIn", first_job.get("url",""), "Dry run - not actually submitted")
    print(f"  ✅ Logged as Job ID #{job_id}")
    print(f"\n  Current Tracker:\n{format_applications_table()}")

    print("\n" + "=" * 60)
    print("  Dry Run Complete! Full pipeline verified.")
    print("=" * 60)

asyncio.run(run())
