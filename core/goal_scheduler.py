import logging
from typing import Optional, List
from core.goal_manager import GoalManager
from core.goal_models import Task, GoalHealth

logger = logging.getLogger("jarvis.goal_scheduler")

class GoalScheduler:
    def __init__(self, manager: GoalManager):
        self.manager = manager
        
    def _is_task_ready(self, task: Task) -> bool:
        """Check if all dependencies are COMPLETED."""
        if not task.dependencies:
            return True
            
        for dep_id in task.dependencies:
            status = self.manager.get_task_status(dep_id)
            if status != GoalHealth.COMPLETED:
                return False
        return True

    def _get_highest_priority_task(self, worker_id: str) -> Optional[Task]:
        tasks = self.manager.get_pending_tasks()
        if not tasks:
            return None
            
        # Filter out blocked tasks
        ready_tasks = []
        for t in tasks:
            if self._is_task_ready(t):
                ready_tasks.append(t)
                
        if not ready_tasks:
            return None
            
        # Mock resource availability (e.g. 1.0 = full resources)
        resource_availability = 1.0
        
        # Sort by mathematical priority descending
        ready_tasks.sort(
            key=lambda t: t.metrics.calculate_priority(resource_availability=resource_availability), 
            reverse=True
        )
        
        # Try to claim tasks in order of priority until we get one
        for top_task in ready_tasks:
            if self.manager.claim_task(top_task.task_id, worker_id):
                return top_task
                
        return None

    def tick(self, worker_id: str = "worker-1") -> Optional[Task]:
        """
        One-shot execution pass. Evaluates priorities, picks top READY task, 
        atomically claims it, and returns it.
        """
        top_task = self._get_highest_priority_task(worker_id)
        if not top_task:
            logger.info("Scheduler tick: No READY pending tasks available.")
            return None
            
        logger.info(f"Scheduler Worker {worker_id} claimed Task {top_task.task_id}")
        return top_task
