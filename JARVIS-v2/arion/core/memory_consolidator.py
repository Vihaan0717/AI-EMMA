# arion/core/memory_consolidator.py

import os
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class MemoryConsolidator:
    """
    The 'Subconscious' of ARION.
    Periodically processes short-term screen learnings into permanent long-term notes.
    Now supports FREE AI Engine (Ollama).
    """
    
    def __init__(self, vault_path: str, ai_engine=None):
        self.vault_path = Path(vault_path)
        self.brain_path = self.vault_path / "Brain"
        self.journal_path = self.vault_path / "Agent_Self" / "Learning_Journal"
        self.ai = ai_engine
        
        self.brain_path.mkdir(parents=True, exist_ok=True)
        self.is_running = False
        print("Memory Consolidator initialized")

    def start(self, interval_hours: int = 6):
        self.is_running = True
        def run_loop():
            while self.is_running:
                try:
                    self.consolidate_memories()
                except Exception as e:
                    print(f"[Consolidator] Error: {e}")
                time.sleep(interval_hours * 3600)
        
        self.thread = threading.Thread(target=run_loop, daemon=True)
        self.thread.start()

    def consolidate_memories(self):
        print("\n[Consolidator] Synthesizing memories...")
        self._consolidate_screen_learnings()

    def _consolidate_screen_learnings(self):
        date_str = datetime.now().strftime('%Y-%m-%d')
        journal_file = self.journal_path / f"{date_str}_screen_learning.md"
        
        if not journal_file.exists(): return

        with open(journal_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip() or not self.ai: return

        try:
            prompt = f"Analyze these screen learning logs and synthesize them into a permanent knowledge note. Group concepts and identifiers. Format AS CLEAN MARKDOWN.\nLogs:\n{content}"
            synthesis = self.ai.generate(prompt, system_prompt="You are ARION's Memory Consolidation Engine.", model=self.ai.primary_model)
            
            filename = f"Reflection_{date_str}.md"
            with open(self.brain_path / filename, 'w', encoding='utf-8') as f:
                f.write(f"---\ntags: [reflection, auto-learning, {date_str}]\n---\n\n{synthesis}")
            print(f"   [Consolidator] Created: {filename}")
        except Exception as e:
            print(f"   [Consolidator] Synthesis failed: {e}")

    def force_reflection(self):
        self.consolidate_memories()
