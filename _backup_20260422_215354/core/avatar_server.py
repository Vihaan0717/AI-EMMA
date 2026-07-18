import asyncio
import websockets
import json
import threading
import queue
import time
from concurrent.futures import ProcessPoolExecutor
from core.logger import get_logger
from agents.vision_agent import VisionTracker
from config.system_config import JarvisConfig
from services.system_watcher import SystemWatcher
from services.api_hub import APIHub
from agents.research_agent import ResearchAgent
from agents.executive_agent import ExecutiveAgent

logger = get_logger("AvatarServer")


# ═══════════════════════════════════════════════════════════════════════
# SUBPROCESS WORKER: Runs DeepFace in a COMPLETELY separate process
# This frees the GIL so the WebSocket server never freezes during scans
# ═══════════════════════════════════════════════════════════════════════
def _biometric_scan_worker(boss_image_path: str, temp_frame_path: str, threshold: float) -> dict:
    """Runs in a separate process. Returns verification results as a plain dict."""
    try:
        from deepface import DeepFace
        result = DeepFace.verify(
            img1_path=boss_image_path,
            img2_path=temp_frame_path,
            model_name="VGG-Face",
            enforce_detection=False
        )
        return {
            "verified": result.get("verified", False),
            "distance": result.get("distance", 1.0),
            "threshold": result.get("threshold", threshold),
            "error": None,
        }
    except Exception as e:
        return {"verified": False, "distance": 1.0, "threshold": threshold, "error": str(e)}


class AvatarServer:
    def __init__(self):
        self.connected_clients = set()
        self.tracker = VisionTracker()
        self.biometric_guard = None  # Set by main.py
        self.toolbox = None          # Set by main.py
        self.loop = None
        self.server = None
        self.server_thread = None
        self.tracking_thread = None
        self.running = False

        # ── THREAD-SAFE BROADCAST QUEUE ──
        # Instead of calling asyncio.run_coroutine_threadsafe() from random threads
        # (which collides with the GIL and causes DNS resolution failures),
        # all threads drop messages into this queue. The event loop drains it safely.
        self._broadcast_queue = queue.Queue()

        # New Services
        self.api_hub = APIHub()
        self.ai_agent = ResearchAgent()
        self.local_ai_agent = ExecutiveAgent()
        self.watcher = None  # Initialized in start()

        # ── PROCESS POOL for CPU-heavy tasks (DeepFace, etc.) ──
        self._process_pool = None

    async def _handler(self, websocket):
        logger.info("New Avatar Client Connected!")
        self.connected_clients.add(websocket)

        # Send initial data
        await self._send_initial_state(websocket)

        try:
            async for message in websocket:
                await self._handle_incoming_message(message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)
            logger.info("Avatar Client Disconnected.")

    async def _send_initial_state(self, websocket):
        """Send weather, news, etc. on connection."""
        data = {
            "type": "INIT_DATA",
            "weather": self.api_hub.get_weather(),
            "news": self.api_hub.get_news(),
            "movies": self.api_hub.get_movies(),
            "system_config": {
                "environment": JarvisConfig.ENVIRONMENT,
                "model": JarvisConfig.LOCAL_MODEL_NAME
            }
        }
        await websocket.send(json.dumps(data))

    async def _handle_incoming_message(self, message_str):
        try:
            data = json.loads(message_str)
            msg_type = data.get("type")

            if msg_type == "PROJECT_COMMAND":
                action = data.get("action")
                params = data.get("parameters", {})
                if self.toolbox:
                    result = self.toolbox.execute_tool(action, params)
                    await self._broadcast({"type": "COMMAND_RESULT", "result": result})

            elif msg_type == "GET_CODE_GEN":
                prompt = data.get("prompt", "Create a python script")
                logger.info(f"UI requested code for: {prompt}")
                # Calling the AI agent in a thread to not block the WebSocket loop
                def run_ai():
                    code_response = self.ai_agent.think(f"Generate a code snippet for: {prompt}. Return ONLY the code block.")

                    if "Sir, I am having trouble connecting to my main cloud servers" in code_response:
                        logger.warning("Cloud servers unavailable in UI. Falling back to local logic core (Ollama)...")
                        code_response = self.local_ai_agent.think(f"Generate a code snippet for: {prompt}. Return ONLY the code block.")

                    # Use the thread-safe queue instead of asyncio.run_coroutine_threadsafe
                    self._enqueue_broadcast({"type": "CODE_RESULT", "code": code_response})

                threading.Thread(target=run_ai, daemon=True).start()

        except Exception as e:
            logger.error(f"Error handling UI message: {e}")

    # ═══════════════════════════════════════════════════════════════
    # THREAD-SAFE BROADCAST SYSTEM
    # Any thread can call _enqueue_broadcast() safely.
    # The asyncio loop drains the queue every 50ms via _drain_queue().
    # ═══════════════════════════════════════════════════════════════
    def _enqueue_broadcast(self, message: dict):
        """Thread-safe: drop a message into the queue for the event loop to broadcast."""
        self._broadcast_queue.put(message)

    async def _drain_queue(self):
        """Continuously drain the broadcast queue from the asyncio event loop."""
        while self.running:
            try:
                while True:
                    msg = self._broadcast_queue.get_nowait()
                    await self._broadcast(msg)
            except queue.Empty:
                pass
            await asyncio.sleep(0.05)  # 50ms drain interval

    def on_os_context_change(self, context):
        """Callback for SystemWatcher. Uses the thread-safe queue."""
        self._enqueue_broadcast(context)

    async def _broadcast(self, message: dict):
        if not self.connected_clients:
            return

        payload = json.dumps(message)
        websockets.broadcast(self.connected_clients, payload)

    def has_clients(self) -> bool:
        """Returns True if there is at least one active WebSocket client."""
        return len(self.connected_clients) > 0

    def trigger_animation(self, action_name: str):
        """Called by JARVIS to send an animation command to the 3D model."""
        logger.info(f"Triggering Animation: {action_name}")
        self._enqueue_broadcast({
            "type": "ANIMATION",
            "action": action_name
        })

    def send_ai_response(self, text: str, emotion: str = "neutral", gesture: str = "idle", style: str = "standard"):
        """Broadcasting AI response metadata for the 3D VRM interface."""
        logger.info(f"Broadcasting AI Response: text='{text[:30]}...', emotion='{emotion}', gesture='{gesture}'")
        self._enqueue_broadcast({
            "type": "AI_RESPONSE",
            "text": text,
            "emotion": emotion,
            "gesture": gesture,
            "style": style
        })

    def trigger_registration_inquiry(self):
        """Audibly asks an unknown guest for their details after Boss approval."""
        msg = "Welcome. My internal records do not yet include your identity. Could you please specify your name and relationship to the Boss?"
        logger.info("Triggering audible registration inquiry.")
        self.send_ai_response(msg, emotion="Joy")
        # In a real system, we'd also trigger the TTS here if the UI doesn't handle it

    def send_audio_command(self, audio_url: str):
        """Tells the frontend to play a specific audio file for lip-sync."""
        logger.info(f"Sending audio play command: {audio_url}")
        self._enqueue_broadcast({
            "type": "PLAY_AUDIO",
            "url": audio_url
        })

    def set_camera_state(self, state: str):
        """Send camera position instructions to the 3D scene."""
        self._enqueue_broadcast({
            "type": "CAMERA_STATE",
            "state": state
        })

    def _start_tracking_loop(self):
        self.tracker.start_camera()
        while self.running:
            data = self.tracker.process_frame()
            if data:
                self._enqueue_broadcast(data)

                if self.biometric_guard:
                    current_time = time.time()
                    last_check = getattr(self.biometric_guard, 'last_scan_time', self.biometric_guard.last_verification_time)
                    if data.get("detected") and (current_time - last_check > 60):
                        # Prevent duplicate checks instantly
                        self.biometric_guard.last_scan_time = current_time

                        # Trigger UI Scan Animation
                        self._enqueue_broadcast({"type": "BIOMETRIC_EVENT", "status": "SCANNING"})

                        def wrap_verify():
                            status = self.biometric_guard.verify_identity(frame=self.tracker.last_frame)
                            self._enqueue_broadcast({"type": "BIOMETRIC_EVENT", "status": status.upper()})
                            
                            if status == "register":
                                self.trigger_registration_inquiry()
                        
                        threading.Thread(target=wrap_verify, daemon=True).start()

            time.sleep(1.0 / 30.0)
        self.tracker.stop_camera()

    def _run_server(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        async def _start_server():
            self.server = await websockets.serve(self._handler, "127.0.0.1", 8765)
            # Start the queue drainer as a background task inside the event loop
            asyncio.ensure_future(self._drain_queue())

        self.loop.run_until_complete(_start_server())
        logger.info("WebSocket Avatar Server running on ws://127.0.0.1:8765")
        self.loop.run_forever()
        self.loop.close()

    def start(self):
        self.running = True

        # Start System Watcher
        self.watcher = SystemWatcher(".", self.on_os_context_change)
        self.watcher.start()

        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

        self.tracking_thread = threading.Thread(target=self._start_tracking_loop, daemon=True)
        self.tracking_thread.start()

    def stop(self):
        self.running = False
        if self.watcher:
            self.watcher.stop()

        if self._process_pool:
            self._process_pool.shutdown(wait=False)

        if self.loop and self.loop.is_running():
            if self.server:
                self.loop.call_soon_threadsafe(self.server.close)
            self.loop.call_soon_threadsafe(self.loop.stop)

        if self.server_thread:
            self.server_thread.join(timeout=3)
        if self.tracking_thread:
            self.tracking_thread.join(timeout=3)


# Global singleton for JARVIS to use
avatar_server_instance = AvatarServer()
