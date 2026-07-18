import asyncio
from datetime import datetime
import os
import logging
import random
import re
from typing import Dict, List, Optional
from pathlib import Path
from nexus.maintenance.glymphatic import GlymphaticGC
from nexus.memory.hebbian_graph import HebbianGraph

logger = logging.getLogger("AutonomousLearner")
# Suppress noisy trafilatura logs
logging.getLogger("trafilatura").setLevel(logging.CRITICAL)
logging.getLogger("htmldate").setLevel(logging.CRITICAL)

class AutonomousLearner:
    """Zero learns continuously in the background, no prompting needed."""
    
    def __init__(self, web_brain, memory, ai_engine):
        self.web = web_brain
        self.memory = memory
        self.ai = ai_engine
        self.interest_graph = {"AI": 1.0, "Robotics": 0.8, "Cybersecurity": 0.7} # topic -> interest_score
        self._running = False
        self._task = None
        
        # Initialize Maintenance Modules
        self.hebbian = HebbianGraph(os.getenv("SUPABASE_DSN", "postgresql://postgres:postgres@localhost:5432/postgres"))
        self.glymphatic = GlymphaticGC(
            qdrant=None, # Will be set by memory manager or via config
            redis_client=None,
            supabase=None,
            hebbian=self.hebbian,
            embedder=self.ai,
            autonomous_learner=self
        )
        
        # Obsidian Vault Connection
        self.vault_path = Path("JARVIS-v2/arion/vault")
        if not self.vault_path.exists():
            self.vault_path = Path("knowledge_vault") # Fallback
        
    async def start(self):
        if self._running: return
        self._running = True
        self._task = asyncio.create_task(self.run_forever())
        asyncio.create_task(self.glymphatic.start())
        logger.info("[AutonomousLearner] Eternal learning loop and Glymphatic GC started.")

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try: await self._task
            except asyncio.CancelledError: pass
        logger.info("[AutonomousLearner] Learning loop stopped.")

    async def run_forever(self):
        """The eternal learning loop."""
        while self._running:
            try:
                # Phase 1: RSS pull (always free, always new)
                await self._absorb_rss()
                
                # Phase 2: Curiosity-driven exploration
                await self._follow_curiosity()
                
                # Phase 3: Knowledge gap filling
                await self._fill_gaps()
                
                # Phase 4: NEW: DMN Idle Exploration
                await self._dmn_idle_exploration()
                
                # Phase 5: NEW: Nightly Glymphatic Cycle (only if hour is late or idle)
                await self._check_nightly_cycle()
                
                # Sleep — but not too long. Random to look natural.
                wait_time = random.uniform(300, 900)
                logger.info(f"[AutonomousLearner] Cycle complete. Sleeping for {wait_time/60:.1f} minutes.")
                await asyncio.sleep(wait_time)
            except Exception as e:
                logger.exception(f"Learning loop error: {e}")
                await asyncio.sleep(60)
                
    async def _absorb_rss(self):
        """Pull RSS feeds, distill new items into memory."""
        logger.info("[AutonomousLearner] Absorbing RSS feeds...")
        items = await self.web.rss.pull_all()
        for item in items:
            if not self._running: break
            # Simple check if already known (relevance query)
            existing = await self.memory.recall(item['title'], limit=1)
            if existing and existing[0].get('relevance', 0) > 0.9:
                continue
            
            # Worth a deep read if high relevance (mocked relevance check)
            full = await self.web.fetcher.fetch(item['url'])
            if full:
                logger.info(f"[AutonomousLearner] Storing new knowledge: {item['title']}")
                await self.memory.remember(f"Article: {item['title']}\nContent: {full['text'][:2000]}", 
                                         importance=0.6, 
                                         metadata={'url': item['url'], 'type': 'news'})
                # Stagger to prevent Ollama overload
                await asyncio.sleep(5) 
                
                # NEW: Sync to Obsidian Knowledge Base
                await self._sync_to_obsidian(item['title'], full['text'], url=item['url'], tags=["news", "auto-learning"])
                    
    async def _follow_curiosity(self):
        """Pick a topic Zero is interested in, explore deeper."""
        if not self.interest_graph or not self._running:
            return
        
        logger.info("[AutonomousLearner] Following curiosity...")
        topics = list(self.interest_graph.keys())
        weights = list(self.interest_graph.values())
        topic = random.choices(topics, weights=weights, k=1)[0]
        
        # Simple question generation (mocked)
        question = f"What are the latest developments in {topic}?"
        result = await self.web.learn(question)
        if result and self._running:
            if 'documents' in result:
                content = "\n".join([doc['text'][:1000] for doc in result['documents'][:2]])
                await self.memory.remember(f"Curiosity Topic: {topic}\n{content}", importance=0.7, metadata={'topic': topic})
            elif 'content' in result:
                await self.memory.remember(f"Curiosity Topic: {topic}\n{result['content']}", importance=0.7, metadata={'topic': topic})
                # NEW: Sync to Obsidian
                await self._sync_to_obsidian(f"Research: {topic}", result['content'], tags=["curiosity", topic])
            
    async def _fill_gaps(self):
        """Analyze memory for unknown concepts and research them."""
        logger.info("[AutonomousLearner] Filling knowledge gaps...")
        pass

    async def _dmn_idle_exploration(self):
        """
        Brain analog: Default Mode Network during rest.
        Builds distant associations and generates hypotheses.
        """
        logger.info("[AutonomousLearner] DMN Idle Exploration: Dreaming...")
        
        # 1. Pick 2 random topics from memory
        topics = list(self.interest_graph.keys())
        if len(topics) < 2: return
        t1, t2 = random.sample(topics, 2)
        
        # 2. Speculate connection
        speculation = f"How might {t1} and {t2} be related in future technologies?"
        logger.info(f"[DMN] Speculating: {speculation}")
        
        # 3. Use AI to brainstorm
        prompt = f"Brainstorm a creative connection between {t1} and {t2}. Keep it grounded but visionary."
        connection = await self.ai.generate(prompt, max_tokens=200, use_fast=True, is_heavy=True)
        
        # 4. Store as a 'dream' or speculative memory
        await self.memory.remember(f"DMN Connection ({t1} + {t2}): {connection}", 
                                 importance=0.4, 
                                 metadata={'type': 'speculation', 'topics': [t1, t2]})

    async def _check_nightly_cycle(self):
        """Triggers the Glymphatic Sweep (Sleep Cycle) for memory consolidation."""
        # Now uses the dedicated GlymphaticGC module
        pass # The loop is handled by glymphatic.start()
                
    def express_interest(self, topic: str, weight: float = 1.0):
        """Called when user shows interest in something."""
        self.interest_graph[topic] = self.interest_graph.get(topic, 0) + weight

    async def _sync_to_obsidian(self, title: str, content: str, url: str = None, tags: List[str] = None):
        """Writes knowledge to the Obsidian vault for visual brain growth."""
        if not self.vault_path.exists(): return
        
        try:
            # Categorize
            folder = self.vault_path / "Knowledge" / "Technology"
            if any(t in title.lower() for t in ["science", "dna", "biology"]):
                folder = self.vault_path / "Knowledge" / "Science"
            elif any(t in title.lower() for t in ["philosophy", "life", "wisdom"]):
                folder = self.vault_path / "Knowledge" / "Philosophy"
            
            folder.mkdir(parents=True, exist_ok=True)
            
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title)[:60]
            filename = f"{datetime.now().strftime('%Y-%m-%d')}_{safe_title}.md"
            filepath = folder / filename
            
            tag_str = "\n".join([f"  - {t}" for t in (tags or [])])
            md_content = f"""---
title: "{title}"
source: {url if url else "Autonomous Research"}
date: {datetime.now().strftime('%Y-%m-%d')}
tags:
{tag_str}
  - auto-injected
---

# {title}

{content[:5000]}

---
*Synthesized by AutonomousLearner*
"""
            filepath.write_text(md_content, encoding='utf-8')
            logger.info(f"[AutonomousLearner] Synced to Obsidian: {filename}")
        except Exception as e:
            logger.error(f"Failed to sync to Obsidian: {e}")
