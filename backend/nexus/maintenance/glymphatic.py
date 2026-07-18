"""
Glymphatic Garbage Collector
Brain analog: glymphatic system + memory consolidation during sleep

Runs:
  • On schedule (default: 03:00 local time daily)
  • On idle trigger (system idle > 30 minutes)

Tasks:
  1. Drop expired Tier 1-2 buffers
  2. Consolidate Hippocampus → Cortex
  3. Apply Hebbian decay & pruning
  4. Deduplicate near-identical embeddings
  5. Remove orphaned references
  6. Trigger DMN idle exploration
"""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np

logger = logging.getLogger("nexus.glymphatic")


class GlymphaticGC:
    # Config
    HOT_TO_COLD_AGE_DAYS = 7
    HOT_TO_COLD_MIN_ACCESS = 3
    HOT_TO_COLD_MIN_EMOTION = 0.7
    DEDUPE_SIMILARITY = 0.97
    SCHEDULED_HOUR = 3                  # 3 AM
    IDLE_TRIGGER_MINUTES = 30

    def __init__(
        self,
        qdrant,
        redis_client,
        supabase,
        hebbian,
        embedder,
        autonomous_learner,         # for DMN exploration
    ):
        self.qdrant = qdrant
        self.redis = redis_client
        self.supabase = supabase
        self.hebbian = hebbian
        self.embedder = embedder
        self.learner = autonomous_learner
        self._running = False

    # -----------------------------------------------------------------
    async def start(self):
        """Launch both schedulers."""
        self._running = True
        await asyncio.gather(
            self._scheduled_loop(),
            self._idle_loop(),
        )

    async def stop(self):
        self._running = False

    # -----------------------------------------------------------------
    async def _scheduled_loop(self):
        """Run full GC at 03:00 every night."""
        while self._running:
            now = datetime.now(timezone.utc)
            next_run = now.replace(
                hour=self.SCHEDULED_HOUR, minute=0, second=0, microsecond=0
            )
            if next_run <= now:
                next_run += timedelta(days=1)
            sleep_seconds = (next_run - now).total_seconds()
            logger.info(f"[Glymphatic] Next scheduled run in {sleep_seconds/3600:.1f}h")
            await asyncio.sleep(sleep_seconds)

            try:
                await self.run_full_cycle()
            except Exception as e:
                logger.exception(f"[Glymphatic] Scheduled cycle failed: {e}")

    # -----------------------------------------------------------------
    async def _idle_loop(self):
        """Trigger lightweight GC after long idle periods."""
        while self._running:
            await asyncio.sleep(300)  # check every 5 min
            try:
                # Mock activity check if redis not fully available
                if not self.redis:
                    continue
                    
                last_activity = await self.redis.get("nexus:last_activity")
                if not last_activity:
                    continue
                last_dt = datetime.fromisoformat(last_activity.decode())
                idle_min = (datetime.now(timezone.utc) - last_dt).total_seconds() / 60
                if idle_min >= self.IDLE_TRIGGER_MINUTES:
                    logger.info(f"[Glymphatic] Idle trigger ({idle_min:.0f}m)")
                    await self.run_light_cycle()
                    # mark activity to prevent repeated triggers
                    await self.redis.set(
                        "nexus:last_activity",
                        datetime.now(timezone.utc).isoformat(),
                    )
            except Exception as e:
                logger.exception(f"[Glymphatic] Idle cycle failed: {e}")

    # =================================================================
    # CYCLES
    # =================================================================
    async def run_full_cycle(self) -> dict:
        """The full nightly 'sleep'. ~5-15 min depending on size."""
        logger.info("=== Glymphatic FULL cycle starting ===")
        start = datetime.now(timezone.utc)
        stats = {}

        stats["expired_dropped"] = await self._drop_expired_buffers()
        stats["consolidated"] = await self._consolidate_hippocampus_to_cortex()
        stats["hebbian"] = await self.hebbian.apply_decay_and_prune()
        stats["deduped"] = await self._dedupe_cortex()
        stats["orphans"] = await self._cleanup_orphans()
        stats["dmn"] = await self._trigger_dmn_exploration()

        duration = (datetime.now(timezone.utc) - start).total_seconds()
        stats["duration_seconds"] = duration
        logger.info(f"=== Glymphatic FULL cycle done in {duration:.1f}s: {stats} ===")

        # Log to Supabase
        if self.supabase:
            try:
                await self.supabase.table("glymphatic_runs").insert({
                    "type": "full",
                    "stats": stats,
                    "ran_at": start.isoformat(),
                    "duration_s": duration,
                }).execute()
            except Exception as e:
                logger.warning(f"Failed to log to Supabase: {e}")
        return stats

    async def run_light_cycle(self) -> dict:
        """Idle-triggered, lightweight."""
        logger.info("=== Glymphatic LIGHT cycle starting ===")
        stats = {
            "expired_dropped": await self._drop_expired_buffers(),
            "hebbian": await self.hebbian.apply_decay_and_prune(),
        }
        logger.info(f"=== Glymphatic LIGHT cycle done: {stats} ===")
        return stats

    # =================================================================
    # TASKS
    # =================================================================
    async def _drop_expired_buffers(self) -> int:
        """Tier 1-2: Redis buffers with TTL already auto-expire."""
        if not self.redis: return 0
        keys = await self.redis.keys("nexus:buffer:*")
        expired = 0
        for k in keys:
            ttl = await self.redis.ttl(k)
            if ttl == -1:  # no TTL set
                await self.redis.delete(k)
                expired += 1
        return expired

    # -----------------------------------------------------------------
    async def _consolidate_hippocampus_to_cortex(self) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.HOT_TO_COLD_AGE_DAYS)
        from qdrant_client.http import models as qm

        promoted = 0
        forgotten = 0
        offset = None

        while True:
            try:
                points, offset = self.qdrant.scroll(
                    collection_name="nexus_hippocampus",
                    scroll_filter=qm.Filter(
                        must=[qm.FieldCondition(
                            key="timestamp",
                            range=qm.DatetimeRange(lt=cutoff.isoformat()),
                        )]
                    ),
                    limit=128,
                    offset=offset,
                    with_payload=True,
                    with_vectors=True,
                )
            except Exception:
                break
                
            if not points:
                break

            for p in points:
                payload = p.payload
                worth_keeping = (
                    payload.get("access_count", 0) >= self.HOT_TO_COLD_MIN_ACCESS
                    or payload.get("emotional_weight", 0) >= self.HOT_TO_COLD_MIN_EMOTION
                    or payload.get("verification_status") == "verified"
                )
                if worth_keeping:
                    new_payload = dict(payload)
                    new_payload["tier"] = "cortex"
                    new_payload["last_reconsolidated"] = datetime.now(timezone.utc).isoformat()
                    new_payload["version"] = payload.get("version", 1) + 1

                    self.qdrant.upsert(
                        collection_name="nexus_cortex",
                        points=[qm.PointStruct(
                            id=p.id,
                            vector=p.vector,
                            payload=new_payload,
                        )],
                    )
                    promoted += 1
                else:
                    forgotten += 1

                self.qdrant.delete(
                    collection_name="nexus_hippocampus",
                    points_selector=qm.PointIdsList(points=[p.id]),
                )

            if offset is None:
                break

        return promoted

    # -----------------------------------------------------------------
    async def _dedupe_cortex(self) -> int:
        """Removes near-identical memory vectors (similarity > DEDUPE_SIMILARITY) from Cortex."""
        deduped = 0
        from qdrant_client.http import models as qm

        offset = None
        while True:
            try:
                points, offset = self.qdrant.scroll(
                    collection_name="nexus_cortex",
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=True
                )
            except Exception as e:
                logger.error(f"[Glymphatic] Scroll failed during dedupe: {e}")
                break

            if not points: 
                break

            for p in points:
                if not p.vector: 
                    continue
                
                try:
                    # Find semantic duplicates
                    hits = self.qdrant.search(
                        collection_name="nexus_cortex",
                        query_vector=p.vector,
                        score_threshold=self.DEDUPE_SIMILARITY,
                        limit=10
                    )
                    
                    # Filter out the original point itself
                    duplicates = [hit.id for hit in hits if hit.id != p.id]
                    
                    if duplicates:
                        self.qdrant.delete(
                            collection_name="nexus_cortex",
                            points_selector=qm.PointIdsList(points=duplicates)
                        )
                        deduped += len(duplicates)
                        logger.info(f"[Glymphatic] Deduped {len(duplicates)} semantic duplicates for memory ID {p.id}")
                except Exception as e:
                    logger.warning(f"[Glymphatic] Search error during dedupe for {p.id}: {e}")
                    
            if offset is None: 
                break
            
        return deduped

    async def _cleanup_orphans(self) -> int:
        """Scrubs vectors that lack fundamental metadata like content and timestamp."""
        orphaned = 0
        from qdrant_client.http import models as qm
        
        offset = None
        while True:
            try:
                points, offset = self.qdrant.scroll(
                    collection_name="nexus_cortex",
                    limit=200,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False # Don't need vectors just for metadata check
                )
            except Exception as e:
                logger.error(f"[Glymphatic] Scroll failed during orphan cleanup: {e}")
                break

            if not points: 
                break
            
            to_delete = []
            for p in points:
                # Essential fields check. For safety and efficiency, we ensure content and timestamp exist.
                # If they are totally empty or null, we drop the vector to prevent retrieval crashes.
                payload = p.payload or {}
                content = payload.get("content", "")
                timestamp = payload.get("timestamp", "")
                
                if not content or not timestamp:
                    to_delete.append(p.id)
                    
            if to_delete:
                try:
                    self.qdrant.delete(
                        collection_name="nexus_cortex",
                        points_selector=qm.PointIdsList(points=to_delete)
                    )
                    orphaned += len(to_delete)
                    logger.info(f"[Glymphatic] Cleaned up {len(to_delete)} malformed orphan vectors.")
                except Exception as e:
                    logger.warning(f"[Glymphatic] Delete error during orphan cleanup: {e}")
                
            if offset is None: 
                break
            
        return orphaned

    async def _trigger_dmn_exploration(self) -> int:
        if self.learner and hasattr(self.learner, '_dmn_idle_exploration'):
            await self.learner._dmn_idle_exploration()
            return 1
        return 0
