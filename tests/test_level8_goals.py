import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.goal_models import Goal, Task, GoalHealth, GoalMetrics, AutonomyBudget
from core.goal_manager import GoalManager
from core.planner import Planner
from core.goal_scheduler import GoalScheduler

@pytest.fixture(autouse=True)
def clean_level8_dbs():
    db_paths = ["logs/test_goals.db"]
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)
    yield
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)

def test_mathematical_priority_scheduler():
    manager = GoalManager(db_path="logs/test_goals.db")
    scheduler = GoalScheduler(manager)
    
    # Task 1: Low urgency, high cost
    t1 = Task(
        goal_id="g1", description="Low priority task",
        metrics=GoalMetrics(importance=1.0, urgency=0.5, estimated_cost=10.0)
    )
    
    # Task 2: High urgency, low cost
    t2 = Task(
        goal_id="g1", description="High priority task",
        metrics=GoalMetrics(importance=1.0, urgency=9.0, estimated_cost=0.5)
    )
    
    manager.add_task_to_goal(t1)
    manager.add_task_to_goal(t2)
    
    top_task = scheduler.tick()
    assert top_task is not None
    assert top_task.task_id == t2.task_id

def test_boundary_enforcement():
    manager = GoalManager(db_path="logs/test_goals.db")
    planner = Planner(manager)
    
    budget = AutonomyBudget(
        allowed_tools=[], allowed_domains=[], max_runtime_seconds=60,
        max_api_calls=100, max_tokens=10000, max_storage_mb=500,
        max_concurrent_workers=5, max_cost_usd=1.0, max_autonomy_depth=3,
        max_tasks=5, max_retries=3
    )
    
    # Exceed task limits
    budget_exceeded = budget.model_copy()
    budget_exceeded.max_tasks = 1
    
    goal = Goal(description="Test goal", budget=budget_exceeded)
    manager.add_goal(goal)
    
    tasks = planner.decompose_goal(goal)
    assert len(tasks) == 0 # Should reject decomposition because it creates 2 tasks

def test_replanning_loop():
    manager = GoalManager(db_path="logs/test_goals.db")
    planner = Planner(manager)
    
    budget = AutonomyBudget(
        allowed_tools=[], allowed_domains=[], max_runtime_seconds=60,
        max_api_calls=100, max_tokens=10000, max_storage_mb=500,
        max_concurrent_workers=5, max_cost_usd=1.0, max_autonomy_depth=3,
        max_tasks=5, max_retries=3
    )
    
    goal = Goal(description="Replanning test", budget=budget)
    manager.add_goal(goal)
    
    # Simulate 3 consecutive task failures for this goal
    manager.update_task_status("t1", goal.goal_id, GoalHealth.FAILED)
    manager.update_task_status("t2", goal.goal_id, GoalHealth.FAILED)
    manager.update_task_status("t3", goal.goal_id, GoalHealth.FAILED)
    
    # Verify Goal Health transitioned to AT_RISK
    conn_path = manager.db_path
    import sqlite3
    db_conn = sqlite3.connect(conn_path)
    c = db_conn.cursor()
    c.execute("SELECT status FROM goals WHERE goal_id = ?", (goal.goal_id,))
    status = c.fetchone()[0]
    assert status == GoalHealth.AT_RISK.value
    
    # Trigger replanner
    planner.replan(goal, "t3")
    
    # Check that an alternative task was added and health is reset
    c.execute("SELECT status FROM goals WHERE goal_id = ?", (goal.goal_id,))
    status = c.fetchone()[0]
    assert status == GoalHealth.HEALTHY.value
    
    c.execute("SELECT count(*) FROM tasks WHERE goal_id = ?", (goal.goal_id,))
    count = c.fetchone()[0]
    assert count == 1 # The alternative task
    
    db_conn.close()
