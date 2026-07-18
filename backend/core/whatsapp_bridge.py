import os
import json
import asyncio
import logging
import subprocess
import time
from pathlib import Path
from core.message_bus import MessageBus, Channel, Message
from core.whatsapp_command_router import WhatsAppCommandRouter
from core.whatsapp_progress_reporter import WhatsAppProgressReporter

logger = logging.getLogger("WhatsAppBridge")

# Temp dir for generated voice note files (shared with Node.js listener)
_ROOT_DIR = Path(__file__).parent.parent.parent
_VOICE_NOTE_DIR = _ROOT_DIR / "JARVIS-v2/arion/data/bridge_queue/temp_media"


class WhatsAppBridge:
    def __init__(self, bus: MessageBus, brain=None):
        self.bus = bus
        self.brain = brain
        # Path to ARION's bridge queue (aligned to project root)
        self.queue_dir = _ROOT_DIR / "JARVIS-v2/arion/data/bridge_queue"
        self.incoming_file = self.queue_dir / "incoming.json"
        self.processing_file = self.queue_dir / "incoming_processing.json"
        self.outgoing_file = self.queue_dir / "outgoing.json"
        self.temp_outgoing = self.queue_dir / "outgoing_temp.json"

        self.running = False
        self._tts_engine = None  # Lazy-loaded KokoroTTSEngine
        self._whisper = None     # Lazy-loaded Whisper STT

        # Command router: handles @mentions, /commands, CRUD, sessions
        self.cmd_router = WhatsAppCommandRouter(brain=self.brain)

        # Progress reporter: pushes proactive notifications to WhatsApp
        self.progress_reporter = WhatsAppProgressReporter(bridge=self, brain=self.brain)

        self._ensure_paths()

    def _ensure_paths(self):
        os.makedirs(self.queue_dir, exist_ok=True)
        os.makedirs(_VOICE_NOTE_DIR, exist_ok=True)
        if not self.incoming_file.exists():
            with open(self.incoming_file, "w") as f:
                json.dump([], f)
        if not self.outgoing_file.exists():
            with open(self.outgoing_file, "w") as f:
                json.dump([], f)

    # ── Lazy load STT/TTS to avoid slowing down boot ──────────────────────
    def _get_tts(self):
        if self._tts_engine is None:
            try:
                from voice.kokoro_engine import KokoroTTSEngine
                self._tts_engine = KokoroTTSEngine()
                logger.info("[WhatsApp] Kokoro TTS loaded for voice note generation.")
            except Exception as e:
                logger.warning(f"[WhatsApp] Kokoro TTS unavailable: {e}")
        return self._tts_engine

    def _get_whisper(self):
        if self._whisper is None:
            try:
                from voice.audio_intelligence import AudioIntelligenceProcessor
                self._whisper = AudioIntelligenceProcessor()
                logger.info("[WhatsApp] Whisper STT loaded for voice note transcription.")
            except Exception as e:
                logger.warning(f"[WhatsApp] Whisper STT unavailable: {e}")
        return self._whisper

    async def start(self):
        self.running = True
        # Keep router brain reference in sync (brain may be set after __init__)
        self.cmd_router.brain = self.brain
        self.progress_reporter.brain = self.brain
        self.bus.subscribe(Channel.WHATSAPP.value, self._handle_bus_message)
        asyncio.create_task(self._poll_incoming())
        # Start proactive progress push loop if enabled
        if os.getenv("WHATSAPP_PROGRESS_PUSH", "true").lower() == "true":
            asyncio.create_task(self.progress_reporter.start())
            logger.info("[WhatsApp] Progress reporter started.")
        logger.info("[WhatsApp] Bridge started. Monitoring queue...")

    async def _poll_incoming(self):
        while self.running:
            try:
                if self.incoming_file.exists():
                    # Atomic read using rename to avoid Windows file locks
                    try:
                        if self.processing_file.exists():
                            os.remove(self.processing_file)
                        os.rename(str(self.incoming_file), str(self.processing_file))
                    except (OSError, FileNotFoundError):
                        await asyncio.sleep(0.5)
                        continue

                    messages = []
                    try:
                        with open(self.processing_file, "r", encoding="utf-8") as f:
                            content = f.read().strip()
                            if content:
                                messages = json.loads(content)
                    except Exception as e:
                        logger.error(f"Read error: {e}")

                    if self.processing_file.exists():
                        os.remove(self.processing_file)

                    if messages:
                        for m in messages:
                            # Process messages sequentially to prevent saturating local Ollama
                            await self._process_single_message(m)

            except Exception as e:
                logger.error(f"Poll error: {e}")

            await asyncio.sleep(1)

    async def _transcribe_voice_note(self, media_path: str) -> str:
        """
        Transcribes a voice note audio file to text using local Whisper STT.
        Returns the transcript, or empty string on failure.
        """
        try:
            whisper = self._get_whisper()
            if not whisper:
                return ""

            logger.info(f"[WhatsApp] Transcribing voice note: {media_path}")
            # Run blocking Whisper call in an executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            segments, info = await loop.run_in_executor(
                None,
                lambda: whisper.model.transcribe(media_path, language=None, task="transcribe")
            )
            transcript = " ".join([s.text for s in segments]).strip()
            logger.info(f"[WhatsApp] Voice note transcript ({info.language}): {transcript[:80]}...")
            return transcript
        except Exception as e:
            logger.error(f"[WhatsApp] Transcription failed: {e}")
            return ""

    def _generate_voice_note(self, text: str, emotion: str = "neutral") -> str | None:
        """
        Generates a voice note OGG/Opus file from text using Kokoro TTS + FFmpeg.

        Pipeline:
          1. Kokoro TTS synthesises the speech to a temporary .wav file.
          2. FFmpeg transcodes the WAV to .ogg (libopus, 48 kHz, mono, 64 kbps) —
             the only format WhatsApp renders as a native voice note bubble.
          3. The temporary .wav is deleted; the .ogg path is returned.

        Returns the .ogg file path on success, None on failure.
        """
        ts = int(time.time())
        wav_path = str(_VOICE_NOTE_DIR / f"jarvis_reply_{ts}.wav")
        ogg_path = str(_VOICE_NOTE_DIR / f"jarvis_reply_{ts}.ogg")
        try:
            tts = self._get_tts()
            if not tts or not tts.is_available:
                logger.warning("[WhatsApp] TTS engine not available, skipping voice note generation.")
                return None

            # Step 1: Synthesise to WAV
            success = tts.synthesize_to_file(text, wav_path, emotion_label=emotion)
            if not success:
                logger.warning("[WhatsApp] Kokoro synthesis returned False. No audio generated.")
                return None

            # Step 2: Transcode WAV → OGG/Opus via FFmpeg
            # WhatsApp requires OGG container + Opus codec to render as a voice note bubble.
            # -y           : overwrite output without prompting
            # -i           : input file
            # -c:a libopus : Opus codec (WhatsApp compatible)
            # -ar 48000    : 48 kHz sample rate (Opus standard)
            # -ac 1        : mono channel (smaller file, adequate for speech)
            # -b:a 64k     : 64 kbps bitrate (clear speech, small file)
            # -vn          : no video stream
            result = subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", wav_path,
                    "-c:a", "libopus",
                    "-ar", "48000",
                    "-ac", "1",
                    "-b:a", "64k",
                    "-vn",
                    ogg_path,
                ],
                capture_output=True,
                timeout=30,
            )

            # Clean up the intermediate WAV regardless of FFmpeg outcome
            try:
                os.remove(wav_path)
            except OSError:
                pass

            if result.returncode != 0:
                err = result.stderr.decode(errors="replace")[-300:]
                logger.error(f"[WhatsApp] FFmpeg conversion failed (rc={result.returncode}): {err}")
                return None

            logger.info(f"[WhatsApp] Voice note (OGG/Opus) generated: {ogg_path}")
            return ogg_path

        except subprocess.TimeoutExpired:
            logger.error("[WhatsApp] FFmpeg conversion timed out after 30s.")
            for p in (wav_path, ogg_path):
                try: os.remove(p)
                except OSError: pass
            return None
        except Exception as e:
            logger.error(f"[WhatsApp] Voice note generation failed: {e}")
            for p in (wav_path, ogg_path):
                try: os.remove(p)
                except OSError: pass
            return None

    def _decide_reply_mode(self, m: dict, response_text: str) -> dict:
        """
        JARVIS decides whether to reply with text, voice, or both.
        Logic:
          - If input was a voice note → always reply with voice note
          - If response is very long (>300 chars) → voice is friendlier, add text summary
          - Otherwise → text only (fast and clear for quick replies)
        Returns a dict: {"text": str|None, "voice": bool}
        """
        was_voice_note = bool(m.get("media_path"))
        response_len = len(response_text)

        if was_voice_note:
            # Mirror: voice in → voice out. Also include text so they can re-read.
            return {"text": None, "voice": True}  # text=None means no separate text bubble
        elif response_len > 400:
            # Long answer: voice note is easier to consume, no extra text bubble needed
            return {"text": None, "voice": True}
        else:
            # Short text reply is clearest
            return {"text": response_text, "voice": False}

    async def _process_single_message(self, m: dict):
        """Worker task to process a single message through the brain"""
        try:
            sender_jid = m.get("jid") or m.get("from") or "unknown"
            sender_name = m.get("name", "Unknown")
            logger.info(f"[WhatsApp] Incoming from {sender_name} ({sender_jid})")

            # ── STEP 1: Transcribe voice note if present ───────────────────
            raw_text = m.get("text", "").strip()
            if m.get("media_path") and os.path.exists(m["media_path"]):
                transcript = await self._transcribe_voice_note(m["media_path"])
                if transcript:
                    raw_text = transcript
                    logger.info(f"[WhatsApp] Using voice transcript as input: {raw_text[:60]}...")
                else:
                    logger.warning("[WhatsApp] Voice note transcription returned empty. Using any text fallback.")
                    raw_text = raw_text or "[Voice note received but could not be transcribed]"

            if not raw_text:
                logger.info("[WhatsApp] No processable text content found. Skipping.")
                return

            if not self.brain:
                logger.warning("[WhatsApp] Brain not initialized.")
                return

            # ── STEP 2: Command Router — @mentions, /commands, sessions ────
            # Touch / Check in with the Watchdog so it knows we are awake
            if self.brain.modules.get('health_watchdog'):
                self.brain.modules['health_watchdog'].check_in()

            routed = await self.cmd_router.route(
                text=raw_text,
                user_jid=sender_jid,
                context=m,
                brain_process_fn=self.brain.process_input,
            )
            if routed is not None:
                # Router handled it — send the response directly
                response_text = routed.get("response", "")
                if response_text:
                    await self._enqueue_outgoing(sender_jid, text=response_text, media_path=None)
                return

            # ── STEP 3: Full NEXUS Brain pipeline ──────────────────────────
            response = await self.brain.process_input(
                raw_input=raw_text,
                source="whatsapp",
                sender=sender_jid,
                context=m
            )

            if not response:
                return

            # ── STEP 3: Collect the full response text ─────────────────────
            response_text = response.get("response", response.get("response_text", ""))
            if not response_text and response.get("bubbles"):
                response_text = " ".join(response["bubbles"])

            if not response_text:
                return

            emotion = response.get("emotion", "neutral")

            # ── STEP 4: JARVIS decides: text, voice, or both ──────────────
            mode = self._decide_reply_mode(m, response_text)
            logger.info(f"[WhatsApp] Reply mode → voice={mode['voice']} text={bool(mode['text'])}")

            media_path = None
            if mode["voice"]:
                # Generate voice note in thread executor (blocking synthesis)
                loop = asyncio.get_event_loop()
                media_path = await loop.run_in_executor(
                    None,
                    lambda: self._generate_voice_note(response_text, emotion)
                )

            # Send voice note (if generated)
            if media_path:
                await self._enqueue_outgoing(sender_jid, text=None, media_path=media_path)
            # Send text bubble (if decided)
            if mode["text"]:
                await self._enqueue_outgoing(sender_jid, text=response_text, media_path=None)
            # Fallback: if voice failed and no text was sent, send text anyway
            if not media_path and not mode["text"]:
                logger.warning("[WhatsApp] Voice note generation failed. Falling back to text reply.")
                await self._enqueue_outgoing(sender_jid, text=response_text, media_path=None)

        except Exception as e:
            logger.error(f"[WhatsApp] Message process error: {e}", exc_info=True)

    async def _enqueue_outgoing(self, target: str, text: str | None, media_path: str | None):
        """Atomically appends to outgoing.json for Node.js to pick up."""
        try:
            out = []
            if self.outgoing_file.exists():
                try:
                    with open(self.outgoing_file, "r", encoding="utf-8") as f:
                        out = json.load(f)
                except Exception:
                    out = []

            entry = {"target": target, "timestamp": time.time()}
            if text:
                entry["text"] = text
            if media_path:
                entry["media_path"] = media_path

            out.append(entry)

            with open(self.temp_outgoing, "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
            os.replace(str(self.temp_outgoing), str(self.outgoing_file))
            logger.info(f"[WhatsApp] Queued outgoing → target={target} voice={bool(media_path)} text={bool(text)}")
        except Exception as e:
            logger.error(f"[WhatsApp] Enqueue error: {e}")

    # Keep legacy send_message for backward compatibility (used by bus handler)
    async def send_message(self, target: str, text: str):
        await self._enqueue_outgoing(target, text=text, media_path=None)

    async def _handle_bus_message(self, msg: Message):
        if msg.event == "send_message":
            target = msg.data.get("target")
            text = msg.data.get("text")
            if target and text:
                await self.send_message(target, text)

    def stop(self):
        self.running = False
