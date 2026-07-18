"""
NEXUS-X OMEGA Background Brain
Handles proactive thinking and memory consolidation
"""

import asyncio
import logging
import queue
import threading

logger = logging.getLogger('BackgroundBrain')

class BackgroundBrain:
    """
    24/7 background thinking process.
    Accepts either a queue.Queue (legacy) or a Dict of modules (new).
    """
    def __init__(self, alert_queue_or_modules=None):
        # Support both old (queue) and new (dict) call signatures
        if isinstance(alert_queue_or_modules, queue.Queue):
            self._alert_queue = alert_queue_or_modules
            self.modules = {}
        elif isinstance(alert_queue_or_modules, dict):
            self._alert_queue = queue.Queue()
            self.modules = alert_queue_or_modules
        else:
            self._alert_queue = queue.Queue()
            self.modules = {}

        self._running = False
        self._thread: threading.Thread = None
        
        # Proactive learning component
        from core.knowledge_consolidator import KnowledgeConsolidator
        self.consolidator = KnowledgeConsolidator()
        
        logger.info("Background Brain initialized")

    def start(self):
        """Start the background brain in a daemon thread."""
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Background Brain started.")

    def stop(self):
        """Stop the background brain."""
        self._running = False
        logger.info("Background Brain stopped.")

    def _run_loop(self):
        """Main loop that processes alerts and background tasks."""
        import time
        last_consolidation = 0
        
        # Initialize consolidator sync loop setup
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self.consolidator.initialize())
        except Exception as e:
            logger.error(f"Failed to pre-warm consolidator in thread: {e}")
        finally:
            loop.close()
            
        while self._running:
            # Drain alert queue
            while True:
                try:
                    alert = self._alert_queue.get_nowait()
                    logger.info(f"[BackgroundBrain] Alert: {alert}")
                    if alert == "run_knowledge_consolidation":
                        logger.info("Manual trigger: running knowledge consolidation cycle...")
                        th_loop = asyncio.new_event_loop()
                        try:
                            th_loop.run_until_complete(self.consolidator.run_consolidation_cycle())
                        except Exception as e:
                            logger.error(f"Manual consolidation trigger failed: {e}")
                        finally:
                            th_loop.close()
                except queue.Empty:
                    break

            # Run consolidator every 1 hour (3600 seconds)
            current_time = time.time()
            if last_consolidation == 0:
                # Set initial timer to run first check 60 seconds after background startup
                last_consolidation = current_time - 3540 
            
            if current_time - last_consolidation > 3600:
                logger.info("Running scheduled proactive knowledge consolidation cycle...")
                th_loop = asyncio.new_event_loop()
                try:
                    th_loop.run_until_complete(self.consolidator.run_consolidation_cycle())
                    last_consolidation = current_time
                except Exception as e:
                    logger.error(f"Scheduled background consolidation cycle failed: {e}")
                finally:
                    th_loop.close()

            # Sleep between cycles
            time.sleep(5)

    async def run_forever(self):
        """Async mode for standalone use."""
        import time
        await self.consolidator.initialize()
        last_consolidation = time.time() - 3540
        while True:
            await asyncio.sleep(60)
            logger.info("Background Brain processing cycle...")
            
            current_time = time.time()
            if current_time - last_consolidation > 3600:
                logger.info("Running proactive knowledge consolidation cycle in async loop...")
                try:
                    await self.consolidator.run_consolidation_cycle()
                    last_consolidation = current_time
                except Exception as e:
                    logger.error(f"Async knowledge consolidation cycle failed: {e}")