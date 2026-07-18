import os
import time
import asyncio
import threading
from fastapi import FastAPI, Request
from core.logger import get_logger
from core.orchestrator import process_telegram_command, telegram_service_instance
from core.telegram_service import TelegramService
from config.system_config import JarvisConfig

logger = get_logger("CloudBackend")

app = FastAPI(title="JARVIS-X Cloud Backend")

# State to track if the Laptop (Edge) is online
# Job Queue and Telephony State
job_queue = []
job_id_counter = 0
call_state = {
    "incoming": False,
    "number": "Unknown",
    "timestamp": 0
}

# Edge State
edge_state = {
    "online": False,
    "last_handshake": 0,
    "ip": "0.0.0.0"
}

@app.on_event("startup")
async def startup_event():
    """Starts the 24/7 Telegram Polling and Telephony Monitoring on boot."""
    logger.info("Starting JARVIS-X Cloud Backend Sentience...")
    
    # Initialize Telegram Service if not already started
    global telegram_service_instance
    if not telegram_service_instance:
        from core.orchestrator import orchestrator
        telegram_service_instance = TelegramService(orchestrator=orchestrator)
        
        def start_telegram_poll():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            telegram_service_instance.loop = loop
            loop.run_until_complete(telegram_service_instance.start())
            loop.run_forever()

        threading.Thread(target=start_telegram_poll, daemon=True).start()
    
    # Start Telephony Agent
    from agents.call_agent import telephony_agent
    telephony_agent.telegram = telegram_service_instance
    asyncio.create_task(telephony_agent.monitor_incoming_calls())
    
    logger.info("Cloud Telegram Polling and Telephony Agent active.")

@app.post("/handshake")
async def handshake(request: Request):
    """Handshake from the Laptop (Edge Agent)."""
    data = await request.json()
    edge_state["online"] = True
    edge_state["last_handshake"] = time.time()
    edge_state["ip"] = request.client.host
    
    logger.info(f"🤝 Handshake active from Laptop: {edge_state['ip']}")
    return {"status": "success", "message": "JARVIS-X Liquid-State Intelligence Synced."}

@app.post("/add_job")
async def add_job(request: Request):
    """Adds a job to the queue for mobile or edge."""
    global job_id_counter
    data = await request.json()
    job_id_counter += 1
    job = {
        "id": job_id_counter,
        "target": data.get("target", "mobile"),
        "type": data.get("type"),
        "params": data.get("params", {}),
        "status": "pending",
        "created_at": time.time()
    }
    job_queue.append(job)
    logger.info(f"🆕 Job added: {job['type']} for {job['target']}")
    return {"status": "success", "job_id": job_id_counter}

@app.get("/get_jobs")
async def get_jobs(target: str = "mobile"):
    """Fetch pending jobs for a specific target."""
    pending = [j for j in job_queue if j["target"] == target and j["status"] == "pending"]
    if pending:
        return {"status": "success", "job": pending[0]}
    return {"status": "success", "job": None}

@app.post("/complete_job")
async def complete_job(request: Request):
    """Marks a job as complete."""
    data = await request.json()
    job_id = data.get("job_id")
    for j in job_queue:
        if j["id"] == job_id:
            j["status"] = "completed"
            j["result"] = data.get("result")
            logger.info(f"✅ Job #{job_id} completed.")
            return {"status": "success"}
    return {"status": "error", "message": "Job not found"}

@app.post("/report_call")
async def report_call(request: Request):
    """Report incoming call from Termux."""
    data = await request.json()
    call_state["incoming"] = data.get("incoming", False)
    call_state["number"] = data.get("number", "Unknown")
    call_state["timestamp"] = time.time()
    logger.info(f"📞 Incoming call reported from: {call_state['number']}")
    return {"status": "success"}

@app.get("/get_call_state")
async def get_call_state():
    """Fetch current telephony state."""
    # Reset state if older than 30s (timeout)
    if time.time() - call_state["timestamp"] > 30:
        call_state["incoming"] = False
    return call_state

@app.get("/status")
async def status():
    return {
        "cloud_status": "online",
        "edge_online": edge_state["online"],
        "last_seen": edge_state["last_handshake"]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
