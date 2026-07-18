import os
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from scraper import fetch_recent_conversations
from refiner import refine_human_context
from db import save_knowledge
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Jarvis Cloud Worker")

def pipeline_job():
    """The core background job: Scrape -> Refine -> Save"""
    logger.info("=== Starting Cloud Pipeline Job ===")
    
    # 1. Scrape
    raw_text = fetch_recent_conversations()
    if not raw_text:
        logger.warning("No data scraped. Aborting pipeline.")
        return

    # 2. Refine
    refined_data = refine_human_context(raw_text)
    if not refined_data:
        logger.warning("Refinement failed. Aborting pipeline.")
        return

    # 3. Save
    success = save_knowledge(refined_data)
    if success:
        logger.info(f"Pipeline finished successfully. Learned: {refined_data.get('human_insight')}")
    else:
        logger.error("Pipeline failed to save to database.")

# Set up the background scheduler
scheduler = BackgroundScheduler()
# Run the pipeline every 60 minutes
scheduler.add_job(pipeline_job, 'interval', minutes=60)

@app.on_event("startup")
def start_scheduler():
    scheduler.start()
    logger.info("Scheduler started. Pipeline will run every 60 minutes.")
    # Run once immediately on startup
    scheduler.add_job(pipeline_job)

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()

@app.get("/")
def read_root():
    return {"status": "Jarvis Cloud Worker is running 24/7."}

@app.get("/health")
def health_check():
    """Endpoint for UptimeRobot to ping"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Render requires binding to 0.0.0.0 and port from env
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
