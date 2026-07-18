import asyncio
import os
import time
from pathlib import Path
from typing import List, Dict, Any

from core.base_agent import BaseAgent
from core.message_bus import Channel, Message, Priority

class IntakeWatcher(BaseAgent):
    def __init__(self, config: dict):
        super().__init__("IntakeWatcher", [Channel.INTAKE])
        self.incoming_root = Path("arion/intake/_incoming")
        self.check_interval = 10.0 # Check every 10 seconds

    async def run_loop(self):
        print(f"[IntakeWatcher] Monitoring {self.incoming_root}...", flush=True)
        self.incoming_root.mkdir(parents=True, exist_ok=True)
        
        while self.running:
            try:
                await self._scan_incoming()
            except Exception as e:
                print(f"[IntakeWatcher] Scan error: {e}", flush=True)
            
            await asyncio.sleep(self.check_interval)

    async def handle_message(self, message: Message):
        if message.action == "trigger_scan":
            await self._scan_incoming()

    async def _scan_incoming(self):
        """Recursively scan _incoming subfolders for new files."""
        for domain_folder in self.incoming_root.iterdir():
            if not domain_folder.is_dir(): continue
            
            domain = domain_folder.name
            for file_path in domain_folder.iterdir():
                if file_path.is_file():
                    await self._process_file(file_path, domain)

    async def _process_file(self, file_path: Path, domain: str):
        print(f"[IntakeWatcher] Found new file: {file_path.name} (Domain: {domain})", flush=True)
        
        # 1. Read file content (basic for now, simplified for EPUB/PDF which need real parsers)
        # ContentRouter would normally handle this, but we'll do simple text/caption check here
        content = ""
        try:
            if file_path.suffix in [".txt", ".md"]:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                content = f"Binary file drop: {file_path.name}"
        except Exception as e:
            print(f"[IntakeWatcher] Read error for {file_path.name}: {e}")

        # 2. Notify Knowledge Engine to ingest
        await self.send(
            to_channel=Channel.KNOWLEDGE,
            action="ingest_content",
            payload={
                "content": content,
                "domain": domain,
                "title": file_path.stem,
                "source_type": "file_drop",
                "file_path": str(file_path)
            },
            priority=Priority.NORMAL
        )

        # 3. Move to processing/trash to avoid re-processing
        # For now, let's keep it in a 'processed' siblings folder
        processed_dir = self.incoming_root.parent / "_processed" / domain
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            new_path = processed_dir / file_path.name
            # Handle collision
            if new_path.exists():
                new_path = processed_dir / f"{int(time.time())}_{file_path.name}"
            
            file_path.rename(new_path)
            print(f"[IntakeWatcher] Moved {file_path.name} to {new_path.relative_to(Path.cwd())}")
        except Exception as e:
            print(f"[IntakeWatcher] Move error for {file_path.name}: {e}")
