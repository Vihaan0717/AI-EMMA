import os
import json
import asyncio
import time
from pathlib import Path
from core.base_agent import BaseAgent
from core.message_bus import Channel, Message

class WhatsAppBridge(BaseAgent):
    def __init__(self, queue_dir: str):
        super().__init__("WhatsAppBridge", [Channel.WHATSAPP])
        self.queue_dir = Path(queue_dir)
        self.incoming_file = self.queue_dir / "incoming.json"
        self.processing_file = self.queue_dir / "incoming_processing.json"
        self.outgoing_file = self.queue_dir / "outgoing.json"
        self.temp_outgoing = self.queue_dir / "outgoing_temp.json"
        
        # Ensure files
        os.makedirs(self.queue_dir, exist_ok=True)
        if not self.incoming_file.exists():
            with open(self.incoming_file, "w") as f: json.dump([], f)
        if not self.outgoing_file.exists():
            with open(self.outgoing_file, "w") as f: json.dump([], f)

    async def run_loop(self):
        print(f"[WhatsAppBridge] Atomic Monitoring: {self.incoming_file.absolute()}")
        
        while self.running:
            try:
                # NUCLEAR ATOMIC READ: Rename file before reading to avoid Windows locking conflicts
                if self.incoming_file.exists():
                    try:
                        # Move to private name
                        os.rename(str(self.incoming_file), str(self.processing_file))
                    except (OSError, FileNotFoundError):
                        # Node might be renaming it right now, skip this millisecond
                        await asyncio.sleep(0.1)
                        continue

                    messages = []
                    with open(self.processing_file, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            try: messages = json.loads(content)
                            except: messages = []

                    # Cleanup processing file
                    if self.processing_file.exists():
                        os.remove(str(self.processing_file))

                    if messages:
                        print(f"[WhatsAppBridge] Processing {len(messages)} incoming messages.")
                        for m in messages:
                            m["source"] = "whatsapp"
                            # Ensure boolean consistency
                            is_owner_val = m.get("isOwner") or m.get("is_owner", False)
                            if is_owner_val == "true" or is_owner_val is True:
                                m["is_owner"] = True
                            else:
                                m["is_owner"] = False
                            
                            contact_id = m.get("jid") or m.get("from") or m.get("contact", "unknown")
                            text_snippet = m.get("text", "")[:30]
                            print(f"[WhatsAppBridge] Forwarding: {contact_id} -> '{text_snippet}...' (owner={m['is_owner']})")

                            await self.send(
                                to_channel=Channel.ORCHESTRATOR,
                                action="process_input",
                                payload=m
                            )
            except Exception as e:
                print(f"[WhatsAppBridge] Atomic Error: {e}")
            
            msg = await self.get_next_message(timeout=1.0)
            if msg:
                await self.handle_message(msg)

    async def handle_message(self, message: Message):
        if message.action == "send_whatsapp":
            target = message.payload.get("target")
            text = message.payload.get("text")
            
            try:
                out = []
                if self.outgoing_file.exists():
                    with open(self.outgoing_file, "r", encoding="utf-8") as f:
                        try: out = json.load(f)
                        except: out = []

                out.append({"target": target, "text": f"{text}", "timestamp": time.time()})
                
                # Atomic Write for Outgoing
                with open(self.temp_outgoing, "w", encoding="utf-8") as f:
                    json.dump(out, f, ensure_ascii=False, indent=2)
                os.replace(str(self.temp_outgoing), str(self.outgoing_file))
                
            except Exception as e:
                print(f"[WhatsAppBridge] Outgoing Error: {e}")
