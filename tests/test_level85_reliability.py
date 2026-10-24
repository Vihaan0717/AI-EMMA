import pytest
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.goal_models import Goal, Task, GoalHealth, AutonomyBudget, GoalMetrics
from core.goal_manager import GoalManager
from core.goal_scheduler import GoalScheduler
from core.recovery_manager import RecoveryManager
from core.planner import Planner

@pytest.fixture(autouse=True)
def clean_level85_dbs():
    db_paths = ["logs/test_reliability.db"]
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)
    yield
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)

def create_mock_budget():
    return AutonomyBudget(
        max_runtime_seconds=600, max_tasks=50, max_retries=3,
        max_api_calls=100, max_tokens=10000, max_storage_mb=500,
        max_concurrent_workers=5, max_cost_usd=5.0, max_autonomy_depth=3,
        allowed_tools=[], allowed_domains=[]
    )

def test_heartbeat_and_reclaim():
    manager = GoalManager(db_path="logs/test_reliability.db")
    scheduler = GoalScheduler(manager)
    recovery = RecoveryManager(manager, heartbeat_timeout_seconds=2.0)
    
    goal = Goal(description="Test heartbeat", budget=create_mock_budget())
    t1 = Task(goal_id=goal.goal_id, description="Task 1")
    goal.tasks.append(t1)
    manager.add_goal(goal)
    
    # Claim the task
    claimed_task = scheduler.tick(worker_id="worker-crash")
    assert claimed_task is not None
    assert claimed_task.task_id == t1.task_id
    
    # Task should be CLAIMED in DB
    assert manager.get_task_status(t1.task_id) == GoalHealth.CLAIMED
    
    # Scan immediately - shouldn't recover because timeout hasn't passed
    assert recovery.scan_and_recover() == 0
    assert manager.get_task_status(t1.task_id) == GoalHealth.CLAIMED
    
    # Simulate time passing (force update last_heartbeat to past)
    import sqlite3
    conn = sqlite3.connect(manager.db_path)
    c = conn.cursor()
    c.execute("UPDATE tasks SET last_heartbeat = ? WHERE task_id = ?", (time.time() - 5.0, t1.task_id))
    conn.commit()
    conn.close()
    
    # Scan again - should recover
    assert recovery.scan_and_recover() == 1
    assert manager.get_task_status(t1.task_id) == GoalHealth.INTERRUPTED

def test_dependency_readiness():
    manager = GoalManager(db_path="logs/test_reliability.db")
    scheduler = GoalScheduler(manager)
    
    goal = Goal(description="Test deps", budget=create_mock_budget())
    t1 = Task(goal_id=goal.goal_id, description="Task 1 (Dependency)")
    t2 = Task(goal_id=goal.goal_id, description="Task 2 (Blocked)", dependencies=[t1.task_id])
    goal.tasks.extend([t1, t2])
    manager.add_goal(goal)
    
    # Tick should return t1
    first_task = scheduler.tick()
    assert first_task.task_id == t1.task_id
    
    # Tick again should return None (t2 is blocked because t1 is not COMPLETED)
    second_task = scheduler.tick()
    assert second_task is None
    
    # Complete t1
    manager.update_task_status(t1.task_id, goal.goal_id, GoalHealth.COMPLETED)
    
    # Now t2 should be available
    third_task = scheduler.tick()
    assert third_task.task_id == t2.task_id

def test_idempotency_key_generation():
    t1 = Task(goal_id="g1", description="Task")
    t1.generate_idempotency_key("upload_file")
    assert t1.idempotency_key == f"g1:{t1.task_id}:upload_file"

def test_mini_chaos_soak():
    manager = GoalManager(db_path="logs/test_reliability.db")
    scheduler = GoalScheduler(manager)
    recovery = RecoveryManager(manager, heartbeat_timeout_seconds=0.1)
    planner = Planner(manager)
    
    goal = Goal(description="Soak test", budget=create_mock_budget())
    manager.add_goal(goal)
    
    for i in range(10):
        manager.add_task_to_goal(Task(goal_id=goal.goal_id, description=f"Soak task {i}"))
        
    for _ in range(5):
        # Claim a task
        t = scheduler.tick(worker_id="soak-worker")
        if t:
            manager.update_task_status(t.task_id, goal.goal_id, GoalHealth.RUNNING)
            # Simulate crash - don't complete it, don't update heartbeat
            
    time.sleep(0.2)
    # Recover all dead tasks
    recovered = recovery.scan_and_recover()
    assert recovered == 5
    
    # Trigger replanner on the first interrupted task to simulate safe retry
    import sqlite3
    conn = sqlite3.connect(manager.db_path)
    c = conn.cursor()
    c.execute("SELECT task_id FROM tasks WHERE status = ?", (GoalHealth.INTERRUPTED.value,))
    interrupted_id = c.fetchone()[0]
    c.fetchall() # clear out remaining rows
    c.close()
    conn.close()
    
    planner.replan(goal, interrupted_id)
    # Validate replan worked
    conn = sqlite3.connect(manager.db_path)
    c = conn.cursor()
    c.execute("SELECT count(*) FROM tasks WHERE goal_id = ?", (goal.goal_id,))
    total_tasks = c.fetchone()[0]
    conn.close()
    
    assert total_tasks == 11 # 10 original + 1 alternative
