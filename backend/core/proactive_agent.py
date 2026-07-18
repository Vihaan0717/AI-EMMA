import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from protocols.morning_briefing import run_morning_briefing
from protocols.end_of_day import run_end_of_day
from core.fleet.goal_manager import goal_manager
from core.fleet.react_engine import react_engine
from core.fleet.personas import FleetPersonas

logger = logging.getLogger("ProactiveAgent")

class ProactiveScheduler:
    """
    Manages all CRON-like tasks and proactive agent interventions, including
    dynamic goal-oriented autonomy (scheduled background tasks).
    """
    def __init__(self, telegram_service=None, ai_engine=None):
        self.scheduler = AsyncIOScheduler()
        self.telegram = telegram_service
        self.ai_engine = ai_engine
        self.personas = FleetPersonas()
        self._bg_task = None

    def start(self):
        logger.info("Initializing Proactive Scheduling Engine...")

        # Schedule Morning Briefing at 8:00 AM every day
        self.scheduler.add_job(
            self._wrap_morning_briefing,
            'cron',
            hour=8,
            minute=0,
            id='morning_briefing'
        )
        
        # Schedule End of Day check-in at 10:00 PM every day
        self.scheduler.add_job(
            self._wrap_end_of_day,
            'cron',
            hour=22,
            minute=0,
            id='end_of_day'
        )

        self.scheduler.start()
        
        # Start the continuous goal/task polling loop
        self._bg_task = asyncio.create_task(self._background_task_loop())
        
        logger.info("Proactive Scheduling Engine started successfully.")

    async def _wrap_morning_briefing(self):
        logger.info("Proactive Trigger: Morning Briefing")
        try:
            await run_morning_briefing(self.telegram)
        except Exception as e:
            logger.error(f"Failed to run morning briefing: {e}")

    async def _wrap_end_of_day(self):
        logger.info("Proactive Trigger: End of Day")
        try:
            await run_end_of_day(self.telegram)
        except Exception as e:
            logger.error(f"Failed to run end of day protocol: {e}")

    async def _background_task_loop(self):
        """Continuously poll GoalManager for scheduled tasks and execute them."""
        logger.info("Goal-Oriented Autonomy background loop started.")
        while True:
            try:
                due_tasks = goal_manager.get_due_tasks()
                for task_record in due_tasks:
                    await self._execute_scheduled_task(task_record)
            except Exception as e:
                logger.error(f"Background task loop error: {e}")
            
            await asyncio.sleep(60)  # Check every 60 seconds

    async def _execute_scheduled_task(self, task_record: dict):
        agent_id = task_record["target_agent"]
        task_id = task_record["id"]
        task_desc = task_record["task"]
        
        logger.info(f"PROACTIVE WAKEUP: Agent '{agent_id}' executing scheduled task '{task_id}'")
        
        if not self.ai_engine:
            logger.warning("AI Engine not available for proactive execution.")
            return

        persona = self.personas.get_persona(agent_id)
        system_prompt = persona["system_prompt"] + "\n\n[PROACTIVE WAKEUP]\nYou have woken up to complete a scheduled background task. Execute it autonomously."
        
        try:
            trace = await react_engine.execute(
                agent_id=agent_id,
                task=task_desc,
                system_prompt=system_prompt,
                ai_engine=self.ai_engine,
                temperature=persona.get("temperature", 0.7)
            )
            
            result_text = trace.final_answer
            goal_manager.mark_task_complete(task_id, result_text)
            
            msg = f"🔔 PROACTIVE ALERT from {agent_id.upper()}:\nTask: {task_desc[:100]}\nResult: {result_text}"
            logger.info(msg)
            
            if self.telegram:
                await self.telegram.send_message(msg)
                
        except Exception as e:
            logger.error(f"Failed to execute scheduled task '{task_id}': {e}")
            goal_manager.mark_task_complete(task_id, f"ERROR: {e}")

    def stop(self):
        logger.info("Stopping Proactive Scheduling Engine...")
        self.scheduler.shutdown()
        if self._bg_task:
            self._bg_task.cancel()
