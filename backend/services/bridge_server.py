import asyncio
import json
import logging
import os
import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, List
from datetime import datetime

# Import NEXUS-X Core
from core.message_bus import MessageBus, Channel, Message
from core.brain import NexusBrain

logger = logging.getLogger("BridgeServer")

app = FastAPI(title="NEXUS-X Bridge Server", version="1.0.0")

# Security: CORS for mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"[Bridge] Client '{client_id}' connected.")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"[Bridge] Client '{client_id}' disconnected.")

    async def send_to_client(self, client_id: str, payload: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(payload))
            except Exception as e:
                logger.error(f"[Bridge] Error sending to {client_id}: {e}")

    async def broadcast(self, payload: dict):
        message = json.dumps(payload)
        for client_id, ws in self.active_connections.items():
            try:
                await ws.send_text(message)
            except:
                pass

manager = ConnectionManager()
brain_instance: NexusBrain = None

# CRUD dynamic state and subscriptions
crud_connections: List[WebSocket] = []
crud_data_store: List[Dict[str, Any]] = [
    {"id": "1", "title": "Quantum Error Correction", "importance": 0.8},
    {"id": "2", "title": "Secure Local Memory Vault", "importance": 0.95},
    {"id": "3", "title": "Obsidian Watchdog Integration", "importance": 0.7}
]
active_agent_name = "Jarvis"
is_thinking_state = False

@app.on_event("startup")
async def startup_event():
    logger.info("[Bridge] WebSocket Spine ready.")


# ── Root route ── browser / Cloudflare verification
@app.get("/")
async def root():
    return {
        "system": "NEXUS-X Zero Protocol",
        "status": "online",
        "brain": "connected" if brain_instance else "initializing",
        "endpoints": {
            "health":    "GET  /status",
            "chat":      "POST /chat       {\"message\": \"...\", \"source\": \"mobile\"}",
            "upload":    "POST /upload     multipart/form-data",
            "websocket": "WS   /ws/{client_id}"
        },
        "flutter_ws_url": "wss://<your-tunnel>.trycloudflare.com/ws/nexus"
    }


# ── REST /chat ── single-shot query for Postman / browser testing
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message", "").strip()
    source = data.get("source", "mobile")

    if not user_input:
        return {"status": "error", "message": "No 'message' field provided."}

    if not brain_instance:
        return {
            "status": "initializing",
            "message": "Cerebral Cortex is still booting. Try again in 30 seconds."
        }

    response = await brain_instance.process_input(user_input, source=source)
    return {
        "status": "ok",
        "agent": response.get("personality", response.get("agent_name", "Jarvis")),
        "reply": response.get("response", response.get("text", "")),
        "emotion": response.get("emotion", "neutral")
    }


# ── POST /context ── Mobile telemetry ingestion
@app.post("/context")
async def ingest_context(request: Request):
    data = await request.json()
    client_id = data.get("client_id", "unknown")
    gps = data.get("gps")
    battery = data.get("battery")
    activity = data.get("activity")
    
    logger.info(f"[Bridge] Context from {client_id}: GPS={gps}, Batt={battery}%, Activity={activity}")
    
    # Pass to brain for proactive analysis if available
    if brain_instance and hasattr(brain_instance, "process_context"):
        asyncio.create_task(brain_instance.process_context(data))
        
    return {"status": "ok", "message": "Context ingested"}



# ── POST /upload ── multimodal ingestion (same as standalone bridge)
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as f:
        f.write(await file.read())
    logger.info(f"[Bridge] Ingesting: {file.filename}")
    if brain_instance and hasattr(brain_instance, 'ingest_multimodal'):
        ok = await brain_instance.ingest_multimodal(file_location)
        if ok and os.path.exists(file_location):
            os.remove(file_location)
        return {"status": "SUCCESS_CLEAR" if ok else "RETRY_SYNC"}
    return {"status": "QUEUED", "message": "File saved. Brain not ready yet."}

# ── POST /vision ── Send photo from mobile for immediate analysis
@app.post("/vision")
async def process_vision(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    file_location = f"uploads/vision_{file.filename}"
    with open(file_location, "wb+") as f:
        f.write(await file.read())
    logger.info(f"[Bridge] Processing vision image: {file.filename}")
    
    if brain_instance and hasattr(brain_instance, 'process_vision'):
        # process_vision should return a text description/analysis of the image
        analysis = await brain_instance.process_vision(file_location)
        return {"status": "ok", "analysis": analysis}
        
    return {"status": "error", "message": "Vision processing not available yet"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    
    # Handshake
    await manager.send_to_client(client_id, {
        "type": "SYSTEM",
        "sender": "NEXUS-X",
        "content": "🔗 Mobile Command Bridge Connected.",
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            user_text = payload.get("content", "")
            
            # Send ACK (Thinking...)
            await manager.send_to_client(client_id, {
                "type": "ACK",
                "sender": "Brain",
                "content": "⚡ NEXUS-X is thinking...",
                "timestamp": datetime.utcnow().isoformat()
            })

            # Process via Brain
            if brain_instance:
                cmd_type = payload.get("type", "COMMAND")
                
                # --- SPECIAL COMMAND HANDLERS ---
                if cmd_type == "MUSIC_CMD":
                    from services.music_service import music_service
                    action = payload.get("action")
                    if action == "pause": music_service.pause()
                    elif action == "resume": music_service.resume()
                    elif action == "skip": music_service.skip()
                    
                    status = music_service.get_status()
                    await manager.send_to_client(client_id, {
                        "type": "MUSIC_STATUS",
                        **status
                    })
                    continue

                if cmd_type == "VOICE_ENROLL":
                    # Future: Trigger voice print recording
                    await manager.send_to_client(client_id, {
                        "type": "SYSTEM",
                        "content": "Voice enrollment feature coming soon. Please record Kanna_Voice_Print.wav manually."
                    })
                    continue
                # -------------------------------

                # Use 'mobile' as source to trigger Arion/Jarvis routing
                response_data = await brain_instance.process_input(
                    raw_input=user_text,
                    source="ui", # Treat as UI/Command source
                    sender=client_id
                )
                
                # Push Response
                await manager.send_to_client(client_id, {
                    "type": "AGENT_RESPONSE",
                    "sender": response_data.get("personality", "NEXUS").upper(),
                    "content": response_data.get("response", ""),
                    "timestamp": datetime.utcnow().isoformat(),
                    "emotion": response_data.get("emotion", "neutral")
                })

                # Broadcast graph update trigger to refresh nodes in real-time
                await manager.broadcast({
                    "type": "GRAPH_UPDATE",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                await manager.send_to_client(client_id, {
                    "type": "ERROR",
                    "content": "Brain not initialized."
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"[Bridge] Error: {e}")
        manager.disconnect(client_id)

@app.websocket("/crud")
async def crud_websocket_endpoint(websocket: WebSocket):
    global is_thinking_state, active_agent_name, crud_data_store
    await websocket.accept()
    crud_connections.append(websocket)
    logger.info("[Bridge] Client subscribed to /crud stream.")
    
    # Send initial state
    try:
        await websocket.send_text(json.dumps({
            "type": "init",
            "activeAgent": active_agent_name,
            "isThinking": is_thinking_state,
            "dataList": crud_data_store,
            "timestamp": datetime.utcnow().isoformat()
        }))
    except Exception as e:
        logger.error(f"[Bridge] Error sending init to crud client: {e}")
        crud_connections.remove(websocket)
        return

    try:
        while True:
            raw = await websocket.receive_text()
            payload = json.loads(raw)
            action = payload.get("action")
            logger.info(f"[Bridge] Received CRUD command: {payload}")

            # Simulate agent thinking & action execution
            is_thinking_state = True
            
            # Broadcast thinking state immediately (optimistic UI sync helper)
            broadcast_payload = {
                "type": "state",
                "activeAgent": active_agent_name,
                "isThinking": True,
                "dataList": crud_data_store
            }
            # Send status update
            for conn in list(crud_connections):
                try:
                    await conn.send_text(json.dumps(broadcast_payload))
                except:
                    pass

            # Small async sleep to simulate processing latency on python backend
            await asyncio.sleep(0.5)

            if action == "create":
                import uuid
                new_item = {
                    "id": str(uuid.uuid4())[:8],
                    "title": payload.get("title", "Unnamed Item"),
                    "importance": float(payload.get("importance", 0.5))
                }
                crud_data_store.append(new_item)
                logger.info(f"[Bridge] Created item: {new_item}")
                
            elif action == "update":
                item_id = payload.get("id")
                updated_title = payload.get("title")
                updated_importance = payload.get("importance")
                for item in crud_data_store:
                    if item["id"] == str(item_id):
                        if updated_title is not None:
                            item["title"] = updated_title
                        if updated_importance is not None:
                            item["importance"] = float(updated_importance)
                        logger.info(f"[Bridge] Updated item: {item}")
                        break
                        
            elif action == "delete":
                item_id = payload.get("id")
                crud_data_store = [item for item in crud_data_store if item["id"] != str(item_id)]
                logger.info(f"[Bridge] Deleted item: {item_id}")

            # Swap agent personality representation on actions to make UI feel alive
            import random
            agents = ["Jarvis", "Hank", "Atlas", "Cleo", "Sentinel", "Arion"]
            active_agent_name = random.choice(agents)
            is_thinking_state = False

            # Broadcast updated store and agent status
            response = {
                "type": "update",
                "activeAgent": active_agent_name,
                "isThinking": is_thinking_state,
                "dataList": crud_data_store,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for conn in list(crud_connections):
                try:
                    await conn.send_text(json.dumps(response))
                except Exception as e:
                    if conn in crud_connections:
                        crud_connections.remove(conn)
                        
    except WebSocketDisconnect:
        if websocket in crud_connections:
            crud_connections.remove(websocket)
        logger.info("[Bridge] Client unsubscribed from /crud stream.")
    except Exception as e:
        logger.error(f"[Bridge] CRUD Socket Error: {e}")
        if websocket in crud_connections:
            crud_connections.remove(websocket)

@app.get("/api/graph")
async def get_graph():
    """
    Returns a unified representation of JARVIS's brain nodes and synapses:
    1. Core Nexus Node
    2. Agents (Hank, Cleo, Arion, etc.)
    3. Health logs (meals, symptoms, mood)
    4. Relational Memory (from MemoryManager Graph)
    5. Universal / Ingested Knowledge Nodes (from SQLite neural_graph.db)
    """
    nodes = []
    links = []
    seen_nodes = set()

    def add_node(node_id: str, label: str, group: str, val: int = 1, details: str = ""):
        if node_id not in seen_nodes:
            seen_nodes.add(node_id)
            nodes.append({
                "id": node_id,
                "label": label,
                "group": group,
                "val": val,
                "details": details
            })

    def add_link(source: str, target: str, label: str = "connected", weight: float = 1.0):
        links.append({
            "source": source,
            "target": target,
            "label": label,
            "weight": weight
        })

    # 1. Central Core Node
    add_node("nexus", "NEXUS Core", "nexus", val=15, details="JARVIS-Nexus Master Core")

    # 2. Fleet Agents
    try:
        from core.fleet.manager import fleet_manager
        personas = fleet_manager.personas.PERSONAS
        for agent_id, info in personas.items():
            name = info.get("name", agent_id.capitalize())
            role = info.get("role", "Agent")
            add_node(f"agent_{agent_id}", name, "agents", val=8, details=f"Role: {role}\nFocus: {info.get('memory_focus', '')}")
            add_link("nexus", f"agent_{agent_id}", "agent_node")
    except Exception as e:
        logger.warning(f"Error loading agents into graph: {e}")

    # 3. Recent Health Logs (Meals, Symptoms, Mood)
    try:
        from core.health_store import health_store
        import datetime
        recent_days = health_store.get_recent_history(limit=7)
        for log in recent_days:
            date_str = log.get("date", "")
            if not date_str:
                continue
            mood = log.get("mood", "neutral")
            plan = log.get("analysis_plan", "")
            
            # Daily Health Node
            health_node_id = f"health_{date_str}"
            add_node(health_node_id, f"Health: {date_str}", "health", val=6, details=f"Mood: {mood}\nMother's Plan: {plan}")
            add_link("nexus", health_node_id, "health_log")

            # Meals Node
            for idx, meal in enumerate(log.get("meals", [])):
                meal_id = f"meal_{date_str}_{idx}"
                items_str = ", ".join(meal.get("items", []))
                time_str = meal.get("time", "Unknown time")
                add_node(meal_id, f"Meal: {items_str}", "meals", val=3, details=f"Time: {time_str}\nPortions: {meal.get('portion_sizes', '')}")
                add_link(health_node_id, meal_id, "consumed")

            # Symptoms Node
            for idx, symptom in enumerate(log.get("symptoms", [])):
                symptom_id = f"symptom_{date_str}_{idx}"
                add_node(symptom_id, f"Symptom: {symptom}", "symptoms", val=4, details=f"Reported on {date_str}")
                add_link(health_node_id, symptom_id, "condition")
    except Exception as e:
        logger.warning(f"Error loading health logs into graph: {e}")

    # 4. Relational Memory (from MemoryManager Graph)
    try:
        if brain_instance and 'memory' in brain_instance.modules:
            mem_graph = brain_instance.modules['memory'].graph.graph
            for node in mem_graph.nodes:
                node_id = f"concept_{node}"
                add_node(node_id, str(node).capitalize(), "concepts", val=5, details="Relational concept in short-term memory")
                
            for u, v, data in mem_graph.edges(data=True):
                relation = data.get("relation", "associates")
                weight = data.get("weight", 1.0)
                add_link(f"concept_{u}", f"concept_{v}", relation, weight)
    except Exception as e:
        logger.warning(f"Error loading relational memories into graph: {e}")

    # 5. Ingested Long Term Knowledge (neural_graph.db)
    try:
        import sqlite3
        db_path = os.path.join(os.getcwd(), "brain", "data", "neural_graph.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch top 50 neurons
            neurons = cursor.execute("SELECT id, label, summary, activation FROM neurons ORDER BY activation DESC LIMIT 50").fetchall()
            for neuron in neurons:
                nid = f"neuron_{neuron['id']}"
                summary = neuron['summary'] or ""
                add_node(nid, neuron['label'], "knowledge", val=4, details=f"Activation: {neuron['activation']:.2f}\n{summary[:200]}")
                
            # Fetch synapses between them
            synapses = cursor.execute("SELECT source_id, target_id, strength FROM synapses LIMIT 100").fetchall()
            for syn in synapses:
                src_id = f"neuron_{syn['source_id']}"
                tgt_id = f"neuron_{syn['target_id']}"
                if src_id in seen_nodes and tgt_id in seen_nodes:
                    add_link(src_id, tgt_id, "synapse", syn['strength'])
            conn.close()
    except Exception as e:
        logger.warning(f"Error loading SQLite neural_graph into graph: {e}")

    return {"nodes": nodes, "links": links}

@app.get("/status")
async def get_status():
    return {
        "status": "online",
        "active_clients": list(manager.active_connections.keys())
    }

# --- STATIC DASHBOARD ---
# Mount the dashboard directory to /ui
dashboard_path = os.path.join(os.getcwd(), "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/ui", StaticFiles(directory=dashboard_path, html=True), name="ui")
    logger.info(f"[Bridge] Dashboard mounted at http://localhost:8000/ui")
else:
    logger.warning("[Bridge] Dashboard directory not found. Skipping static mount.")

def start_bridge_server(brain: NexusBrain, host: str = "0.0.0.0", port: int = 8000):
    """Blocking entry point."""
    global brain_instance
    brain_instance = brain
    uvicorn.run(app, host=host, port=port, log_level="info")

async def run_bridge_async(brain: NexusBrain, host: str = "0.0.0.0", port: int = 8000):
    """Non-blocking async task. Guardian guarantees port is free before spawning us."""
    global brain_instance
    brain_instance = brain
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            config = uvicorn.Config(app, host=host, port=port, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()
            break  # Success
        except (SystemExit, OSError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"[Bridge] Port {port} still busy (attempt {attempt+1}/{max_retries}). Waiting 3s...")
                await asyncio.sleep(3)
            else:
                logger.error(f"[Bridge] Failed to bind port {port} after {max_retries} attempts. Exiting.")
                import sys
                sys.exit(1)  # Signal Guardian to restart us
        except Exception as e:
            if "10048" in str(e) and attempt < max_retries - 1:
                logger.warning(f"[Bridge] Port {port} still busy (attempt {attempt+1}/{max_retries}). Waiting 3s...")
                await asyncio.sleep(3)
            else:
                raise

def _kill_port_occupant(port: int):
    """Legacy stub — Guardian now handles port clearing. No-op."""
    pass

