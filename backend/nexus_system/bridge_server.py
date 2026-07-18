import sys
import os
import json
import asyncio
import subprocess
from fastapi import FastAPI, Request, WebSocket, UploadFile, File, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from voice.audio_intelligence import AudioIntelligenceProcessor

# --- PORT GUARDIAN: Zero-Conflict Layer ---
def clear_port(port):
    """Automatically finds and kills any process using the target port."""
    try:
        cmd = f'netstat -ano | findstr :{port}'
        output = subprocess.check_output(cmd, shell=True).decode()
        for line in output.strip().split('\n'):
            if "LISTENING" in line:
                pid = line.strip().split()[-1]
                if int(pid) != os.getpid():
                    print(f"[PortGuardian] Port {port} is taken by PID {pid}. Clearing it...")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
    except Exception:
        pass

clear_port(8000)
# ------------------------------------------

# 1. Cerebral Link to JARVIS_Project
MAIN_PATH = r'C:\Users\anger\Desktop\JARVIS_Project'
if MAIN_PATH not in sys.path:
    sys.path.append(MAIN_PATH)

app = FastAPI(
    title="NEXUS-X Zero Bridge",
    description="Mobile Command Bridge — Zero Protocol",
    version="2.0.0"
)

# CORS: allow Cloudflare tunnel origin and local Flutter web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for the brain
nexus = None
brain = None
audio_processor = AudioIntelligenceProcessor()

@app.on_event("startup")
async def startup_event():
    """Initialize the Full Intelligence Pipeline on startup."""
    global nexus, brain
    os.environ["DISABLE_BRIDGE"] = "true"  # Prevent port conflict with JARVIS internal bridge
    try:
        from main import NexusSystem  # Main orchestrator from JARVIS_Project

        print("[NEXUS-X] Initializing Cerebral Cortex...")
        nexus = NexusSystem()
        await nexus.initialize()
        brain = nexus.brain
        audio_processor.start()
        print("[NEXUS-X] Cerebral Connection Established. Zero Protocol ACTIVE.")
    except Exception as e:
        print(f"[NEXUS-X] Connection Failed: {e}. Check path: {MAIN_PATH}")


# 2. Root route — browser verification (visit / to confirm Zero Protocol is alive)
@app.get("/")
async def root():
    return {
        "system": "NEXUS-X Zero Protocol",
        "status": "online",
        "brain": "connected" if brain else "initializing",
        "endpoints": {
            "health":    "GET  /status",
            "chat":      "POST /chat       {\"message\": \"...\", \"source\": \"mobile\"}",
            "upload":    "POST /upload     multipart/form-data",
            "websocket": "WS   /ws/nexus"
        },
        "flutter_ws_url": "wss://<your-tunnel>.trycloudflare.com/ws/nexus"
    }


# 3. Health Check — machine-readable ping
@app.get("/status")
async def status():
    return {
        "status": "online",
        "brain": "connected" if brain else "initializing",
        "system": "NEXUS-X Zero Protocol",
        "host_binding": "0.0.0.0:8000"
    }


# 4. REST /chat — single-shot query (useful for Postman / browser testing)
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "").strip()
    source = data.get("source", "mobile")

    if not user_input:
        return {"status": "error", "message": "No 'message' field provided."}

    if not brain:
        return {
            "status": "initializing",
            "message": "Cerebral Cortex is still booting. Try again in 30 seconds."
        }

    response = await brain.process_input(user_input, source=source)
    return {
        "status": "ok",
        "agent": response.get("agent_name", "Jarvis"),
        "reply": response.get("text", ""),
        "emotion": response.get("emotion", "neutral")
    }


# 5. Multimodal Ingestion Layer (A15)
@app.post("/upload")
async def handle_ingestion(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)

    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())

    print(f"[NEXUS-X] Ingesting: {file.filename}...")

    if brain:
        analysis_result = await brain.ingest_multimodal(file_location)
    else:
        analysis_result = None

    if analysis_result:
        if os.path.exists(file_location):
            os.remove(file_location)  # The "Forget" step
        return {
            "status": "SUCCESS_CLEAR", 
            "message": "Knowledge synced to Main Memory.",
            "analysis": analysis_result
        }
    return {"status": "RETRY_SYNC"}

# 6. Behavioral Ingestion Layer (Accessibility Hooks)
@app.post("/behavior")
async def handle_behavior(request: Request):
    data = await request.json()
    app_package = data.get("package", "unknown")
    screen_text = data.get("text", "")
    
    if nexus and nexus.behavior_observer:
        await nexus.behavior_observer.process_screen_event(app_package, screen_text)
        return {"status": "ACKNOWLEDGED"}
    return {"status": "INTERNAL_CORTEX_MISSING"}


# 4. The 24/7 War Room (WebSocket)
@app.websocket("/ws/nexus")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Send connection handshake so Flutter knows we're alive
    await websocket.send_text(json.dumps({
        "sender": "NEXUS-X",
        "content": "Zero Protocol Bridge Connected. All systems online.",
        "type": "SYSTEM"
    }))
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            user_input = message.get('content', '')

            if not brain:
                await websocket.send_text(json.dumps({
                    "sender": "System",
                    "content": "Cerebral Cortex is still initializing. Try again in 30 seconds.",
                    "type": "ERROR"
                }))
                continue

            # Process through the real A1-A8 Cognitive Pipeline
            ai_response = await brain.process_input(user_input, source="ui")

            await websocket.send_text(json.dumps({
                "sender": ai_response.get("agent_name", "Jarvis"),
                "content": ai_response.get("text", ""),
                "emotion": ai_response.get("emotion", "neutral"),
                "type": "AGENT_RESPONSE"
            }))
    except Exception as e:
        print(f"[NEXUS-X] WebSocket disconnected: {e}")


# 5. The VoIP Spine (Audio Streaming)
@app.websocket("/ws/audio")
async def audio_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("[NEXUS-X] VoIP Audio Stream Connected.")
    try:
        while True:
            # Receive binary audio chunks (16-bit PCM)
            data = await websocket.receive_bytes()
            audio_processor.add_audio_chunk(data)
    except WebSocketDisconnect:
        print("[NEXUS-X] VoIP Audio Stream Disconnected.")
    except Exception as e:
        print(f"[NEXUS-X] Audio Stream Error: {e}")


if __name__ == "__main__":
    import uvicorn
    # ⚠️  CRITICAL: host="0.0.0.0" is REQUIRED for Cloudflare tunnel to work.
    #    host="127.0.0.1" would give "connection refused" from the tunnel.
    print("[NEXUS-X] Starting Zero Bridge on 0.0.0.0:8000")
    print("[NEXUS-X] Cloudflare tunnel should point to: http://127.0.0.1:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")