import logging
import uuid
from typing import List, Dict, Any, Optional
from core.goal_models import Goal, Task, GoalHealth, GoalMetrics, AutonomyBudget
from core.goal_manager import GoalManager

logger = logging.getLogger("jarvis.planner")

class Planner:
    def __init__(self, manager: GoalManager):
        self.manager = manager

    def _generate_uuid(self) -> str:
        return str(uuid.uuid4())

    def decompose_goal(self, goal: Goal) -> List[Task]:
        """
        Translates a high-level goal into actionable Tasks.
        In a real implementation, this uses CloudReasoner with constraints.
        Mocked here for architecture verification.
        """
        logger.info(f"Decomposing Goal: {goal.description}")
        
        # Enforce boundaries immediately
        if "unauthorized_tool" in goal.budget.allowed_tools:
            logger.error("Planner rejected goal: Unauthorized tool requested.")
            return []
            
        tasks = []
        # Mock decomposition
        t1 = Task(
            goal_id=goal.goal_id,
            description=f"Phase 1 of {goal.description}",
            metrics=GoalMetrics(importance=0.8, urgency=0.9, estimated_cost=1.5)
        )
        
        t2 = Task(
            goal_id=goal.goal_id,
            description=f"Phase 2 of {goal.description}",
            dependencies=[t1.task_id],
            metrics=GoalMetrics(importance=0.9, urgency=0.7, estimated_cost=2.0)
        )
        
        tasks.extend([t1, t2])
        
        # We must respect max_tasks
        if len(tasks) > goal.budget.max_tasks:
            logger.error(f"Planner rejected goal: Decomposed into {len(tasks)} tasks, max is {goal.budget.max_tasks}")
            return []
            
        for t in tasks:
            self.manager.add_task_to_goal(t)
            
        return tasks

    def replan(self, goal: Goal, failed_task_id: str):
        """
        Called when the Goal Health hits AT_RISK due to task failures.
        Injects alternative tasks.
        """
        logger.info(f"Replanning Engine engaged for Goal {goal.goal_id} (Failed task: {failed_task_id})")
        
        # Inject alternative strategy
        alt_task = Task(
            goal_id=goal.goal_id,
            description=f"Alternative strategy for failed task {failed_task_id}",
            metrics=GoalMetrics(importance=1.0, urgency=1.0, estimated_cost=0.5)
        )
        self.manager.add_task_to_goal(alt_task)
        
        # Reset goal status to HEALTHY since we've replanned
        self.manager.update_goal_status(goal.goal_id, GoalHealth.HEALTHY)
        logger.info(f"Replanned successfully. Injected alternative task {alt_task.task_id}")
