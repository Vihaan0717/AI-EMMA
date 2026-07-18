import asyncio
import os
import json
import aiohttp
import aiofiles
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from core.base_agent import BaseAgent
from core.message_bus import Channel, Message, Priority

class TelegramCenter(BaseAgent):
    # ── File size limits ─────────────────────────────────────────────
    MAX_FILE_SIZE_MB = 2000  # Telegram allows up to 2GB

    # ── Domain hint keywords in captions ────────────────────────────
    CAPTION_DOMAIN_MAP = {
        "book":       "books",
        "novel":      "books",
        "story":      "books",
        "philosophy": "philosophy",
        "philo":      "philosophy",
        "history":    "history",
        "religion":   "religion_beliefs",
        "science":    "science_biology_math",
        "bio":        "science_biology_math",
        "tech":       "computer_science_tech",
        "code":       "computer_science_tech",
        "music":      "music",
        "song":       "music",
        "anime":      "anime",
        "movie":      "movies_series",
        "film":       "movies_series",
        "series":     "movies_series",
        "show":       "movies_series",
        "psychology": "psychology_human_nature",
        "psych":      "psychology_human_nature",
        "general":    "general",
    }

    # ── MIME type → folder mapping ───────────────────────────────────
    MIME_FOLDER_MAP = {
        "application/pdf":                 "books",
        "application/epub+zip":            "books",
        "text/plain":                      "general",
        "text/markdown":                   "general",
        "audio/mpeg":                      "music",
        "audio/mp4":                       "music",
        "audio/flac":                      "music",
        "audio/ogg":                       "music",
        "audio/wav":                       "music",
        "video/mp4":                       "movies",
        "video/x-matroska":                "movies",
        "image/jpeg":                      "general",
        "image/png":                       "general",
        "application/vnd.openxmlformats": "general",
    }

    def __init__(self, config: dict):
        super().__init__("TelegramCenter", [Channel.TELEGRAM])
        self.token         = config.get("telegram_token", "")
        self.owner_chat_id = config.get("telegram_owner_chat_id", "")
        self.base_url      = f"https://api.telegram.org/bot{self.token}"
        self.file_url      = f"https://api.telegram.org/file/bot{self.token}"
        self.last_update   = 0
        self.session: Optional[aiohttp.ClientSession] = None

    async def run_loop(self):
        print("[TelegramCenter] Bot active. Polling for messages...", flush=True)
        if not self.token:
            print("[TelegramCenter] WARNING: telegram_token is empty. Bot will not function.", flush=True)
        
        self.session = aiohttp.ClientSession()
        
        while self.running:
            if self.token:
                try:
                    await self._poll_updates()
                except Exception as e:
                    print(f"[TelegramCenter] Poll error: {e}", flush=True)
            
            # Handle bus messages
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def stop(self):
        if self.session:
            await self.session.close()
        await super().stop()

    async def handle_message(self, message: Message):
        """Handle internal bus messages (send_alert, etc.)."""
        action = message.action
        if action == "send_alert":
            text = message.payload.get("message", "")
            await self.send_message(f"🚨 *System Alert*:\n{text}")
        
        elif action == "privacy_request":
            # New: Alert with buttons for privacy decisions
            payload = message.payload
            await self.send_alert_with_buttons(
                text=f"🔒 *Privacy Request*\n{payload.get('message')}",
                contact=payload.get("contact"),
                topic=payload.get("topic")
            )
            
        elif action == "send_whatsapp_relay":
            # Relay WhatsApp messages to Telegram for viewing
            payload = message.payload
            text = f"📱 *WhatsApp from {payload.get('sender')}*:\n{payload.get('text')}"
            await self.send_message(text)

        elif action == "send_reply":
            text = message.payload.get("text", "")
            await self.send_message(text)

    # ── Polling ──────────────────────────────────────────────────────

    async def _poll_updates(self):
        params = {"offset": self.last_update + 1, "timeout": 10}
        async with self.session.get(f"{self.base_url}/getUpdates", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                for update in data.get("result", []):
                    self.last_update = update["update_id"]
                    await self._handle_update(update)

    async def _handle_update(self, update: dict):
        if "callback_query" in update:
            await self._handle_callback(update["callback_query"])
            return
            
        msg = update.get("message", {})
        if not msg: return
        
        chat_id = str(msg.get("chat", {}).get("id", ""))
        
        # Security: If owner_chat_id is empty, the first person to message becomes owner (Initial setup)
        if not self.owner_chat_id:
            self.owner_chat_id = chat_id
            print(f"[TelegramCenter] Initialized Owner Chat ID: {chat_id}", flush=True)
            await self.send_message(f"✅ Owner identified! ID: `{chat_id}`\nSaved to session. Update your config to make it permanent.")

        if chat_id != str(self.owner_chat_id): return

        if "document" in msg: await self._handle_document(msg)
        elif "audio" in msg:  await self._handle_audio(msg)
        elif "voice" in msg:  await self._handle_voice(msg)
        elif "video" in msg:  await self._handle_video(msg)
        elif "photo" in msg:  await self._handle_photo(msg)
        elif "text" in msg:   await self._handle_text(msg)

    # ── Handlers ──────────────────────────────────────────────────────

    async def _handle_document(self, msg: dict):
        doc = msg["document"]
        file_id = doc["file_id"]
        filename = doc.get("file_name", f"doc_{int(time.time())}")
        mime = doc.get("mime_type", "")
        caption = msg.get("caption", "")
        
        domain = self._detect_domain_from_caption(caption)
        if domain == "general": domain = self.MIME_FOLDER_MAP.get(mime, "general")
        
        await self.send_message(f"📥 Downloading `{filename}`...\nDomain: `{domain}`")
        path = await self._download_file(file_id, filename, domain)
        if path: await self.send_message(f"✅ Saved to intake: `{filename}`")

    async def _handle_text(self, msg: dict):
        text = msg.get("text", "").strip()
        tl = text.lower()
        
        # 1. Commands
        if tl in ["/status", "status"]: await self._cmd_status()
        elif tl in ["/vault", "vault"]: await self._cmd_vault_summary()
        elif tl in ["/queue", "queue"]: await self._cmd_show_queue()
        elif tl.startswith("learn "): await self._handle_learn(text)
        elif text.startswith("http"): await self._handle_url(text)
        elif tl.startswith("allow "): await self._handle_allow(text)
        
        # 2. General conversation -> Orchestrator
        else:
            await self.send(
                to_channel=Channel.ORCHESTRATOR,
                action="process_input",
                payload={
                    "text": text,
                    "contact": "owner_telegram",
                    "source": "telegram",
                    "is_owner": True,
                    "jid": self.owner_chat_id
                }
            )

    async def _handle_learn(self, text: str):
        # Forward to Orchestrator's new learn handler
        await self.send(
            to_channel=Channel.ORCHESTRATOR,
            action="process_input",
            payload={
                "text": text,
                "contact": "owner_telegram",
                "source": "telegram",
                "is_owner": True
            }
        )

    async def _handle_url(self, url: str):
        await self.send_message(f"🌐 Processing URL...")
        await self.send(
            to_channel=Channel.KNOWLEDGE,
            action="ingest_url",
            payload={"url": url}
        )

    # ── Commands ──────────────────────────────────────────────────────

    async def _cmd_status(self):
        # We need to request this from the Monitor agent
        await self.send(to_channel=Channel.MONITOR, action="get_status", payload={"reply_to": "telegram"})

    async def _cmd_vault_summary(self):
        # Simple directory listing for now
        v_path = Path("arion/vault/Knowledge")
        if not v_path.exists():
            await self.send_message("📚 Vault empty.")
            return
        
        summary = "📚 *Knowledge Vault Summary*:\n"
        for d in v_path.iterdir():
            if d.is_dir():
                count = len(list(d.glob("*.md")))
                summary += f"- {d.name}: {count} nodes\n"
        await self.send_message(summary)

    async def _cmd_show_queue(self):
        q_path = Path("arion/data/learning_queue.json")
        if not q_path.exists():
            await self.send_message("📭 Queue empty.")
            return
        with open(q_path, "r") as f:
            q = json.load(f)
        pending = [i for i in q if i["status"] == "queued"]
        await self.send_message(f"📋 *Learning Queue*: {len(pending)} pending items.")

    # ── Download Logic ────────────────────────────────────────────────

    async def _download_file(self, file_id: str, filename: str, domain: str) -> Optional[str]:
        try:
            async with self.session.get(f"{self.base_url}/getFile", params={"file_id": file_id}) as resp:
                data = await resp.json()
                file_path = data["result"]["file_path"]
            
            save_dir = Path("arion/intake/_incoming") / domain
            save_dir.mkdir(parents=True, exist_ok=True)
            save_path = save_dir / "".join(c for c in filename if c not in r'\/:*?"<>|')
            
            async with self.session.get(f"{self.file_url}/{file_path}") as resp:
                async with aiofiles.open(save_path, "wb") as f:
                    await f.write(await resp.read())
            return str(save_path)
        except Exception as e:
            print(f"[TelegramCenter] Download error: {e}", flush=True)
            return None

    # ── Message Sending ───────────────────────────────────────────────

    async def send_message(self, text: str, reply_markup: dict = None):
        if not self.session or not self.owner_chat_id: return
        payload = {"chat_id": self.owner_chat_id, "text": text, "parse_mode": "Markdown"}
        if reply_markup: payload["reply_markup"] = json.dumps(reply_markup)
        
        try:
            async with self.session.post(f"{self.base_url}/sendMessage", json=payload) as resp:
                return await resp.json()
        except Exception as e:
            print(f"[TelegramCenter] Send error: {e}", flush=True)

    async def send_alert_with_buttons(self, text: str, contact: str, topic: str):
        kb = {"inline_keyboard": [[
            {"text": "✅ Allow", "callback_data": f"allow:{contact}:{topic}"},
            {"text": "🚫 Deny", "callback_data": f"deny:{contact}:{topic}"}
        ]]}
        await self.send_message(text, reply_markup=kb)

    async def _handle_callback(self, callback: dict):
        data = callback.get("data", "")
        chat_id = str(callback["from"]["id"])
        if chat_id != str(self.owner_chat_id): return
        
        if data.startswith("allow:"):
            _, contact, topic = data.split(":")
            await self.send(Channel.ORCHESTRATOR, "process_input", {"text": f"allow {contact} {topic}", "is_owner": True})
            await self.send_message(f"✅ Approved: {contact} can access {topic}")
        elif data.startswith("deny:"):
            await self.send_message(f"🚫 Denied.")

    def _detect_domain_from_caption(self, caption: str) -> str:
        if not caption: return "general"
        cl = caption.lower()
        for k, v in self.CAPTION_DOMAIN_MAP.items():
            if k in cl: return v
        return "general"
