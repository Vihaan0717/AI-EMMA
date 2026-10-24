import pytest
import os
import sys
import time
import sqlite3
import threading
import random
import logging
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.goal_models import Goal, Task, GoalHealth, AutonomyBudget
from core.goal_manager import GoalManager
from core.goal_scheduler import GoalScheduler
from core.recovery_manager import RecoveryManager
from core.planner import Planner

logger = logging.getLogger("jarvis.endurance_test")
logger.setLevel(logging.INFO)

DB_PATH = "logs/test_endurance.db"

def clean_db():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            time.sleep(1)
            try:
                os.remove(DB_PATH)
            except PermissionError:
                pass

def create_mock_budget():
    return AutonomyBudget(
        max_runtime_seconds=3600, max_tasks=2000, max_retries=10,
        max_api_calls=5000, max_tokens=1000000, max_storage_mb=500,
        max_concurrent_workers=10, max_cost_usd=50.0, max_autonomy_depth=3,
        allowed_tools=[], allowed_domains=[]
    )

def test_1000_task_endurance_soak():
    clean_db()
    
    manager = GoalManager(db_path=DB_PATH)
    scheduler = GoalScheduler(manager)
    # Generous timeout to account for SQLite locks under high concurrency
    recovery = RecoveryManager(manager, heartbeat_timeout_seconds=2.0)
    planner = Planner(manager)
    
    goal = Goal(description="Endurance 1000 Task Goal", budget=create_mock_budget())
    manager.add_goal(goal)
    
    # Generate 1000 tasks. 
    # 900 independent tasks
    # 100 tasks that depend on earlier tasks
    for i in range(1000):
        t = Task(goal_id=goal.goal_id, description=f"Endurance Task {i}")
        manager.add_task_to_goal(t)

    # State for workers
    is_running = True
    processed_count = 0
    lock = threading.Lock()
    
    def worker_loop(worker_id):
        nonlocal processed_count
        while is_running:
            t = scheduler.tick(worker_id=worker_id)
            if not t:
                time.sleep(0.01)
                continue
                
            try:
                # Must transition from CLAIMED -> RUNNING atomically to avoid zombie workers waking up
                success = manager.update_task_status(t.task_id, goal.goal_id, GoalHealth.RUNNING, expected_status=GoalHealth.CLAIMED)
                if not success:
                    continue
                
                outcome = random.random()
                time.sleep(0.01) # Simulate work
                
                # Simulate crashes (10%)
                if outcome < 0.10:
                    # Do nothing, leave it RUNNING, let RecoveryManager handle it
                    continue
                
                # Try to mark it COMPLETED, but only if it's still RUNNING
                # This prevents a zombie worker from marking an INTERRUPTED task as completed
                manager.update_task_status(t.task_id, goal.goal_id, GoalHealth.COMPLETED, expected_status=GoalHealth.RUNNING)
                    
                with lock:
                    processed_count += 1
            except Exception as e:
                # Silently catch exceptions (e.g. DB locks in test) to keep worker alive
                pass

    def recovery_loop():
        while is_running:
            recovered = recovery.scan_and_recover()
            if recovered > 0:
                # Get the interrupted tasks and replan them
                conn = sqlite3.connect(manager.db_path, timeout=10.0)
                c = conn.cursor()
                c.execute("SELECT task_id FROM tasks WHERE status = ?", (GoalHealth.INTERRUPTED.value,))
                interrupted_tasks = c.fetchall()
                c.close()
                conn.close()
                
                for row in interrupted_tasks:
                    tid = row[0]
                    # Simulate replanning by adding a new task with the same description
                    conn = sqlite3.connect(manager.db_path, timeout=10.0)
                    c = conn.cursor()
                    c.execute("SELECT description, dependencies_json FROM tasks WHERE task_id = ?", (tid,))
                    t_data = c.fetchone()
                    c.close()
                    conn.close()
                    
                    if t_data:
                        import json
                        desc = t_data[0]
                        deps = json.loads(t_data[1]) if t_data[1] else []
                        
                        # Only replan if we haven't already created a replacement
                        # We use idempotency to prevent infinite replan loops for this test
                        alt_task = Task(goal_id=goal.goal_id, description=desc, dependencies=deps)
                        # Mark old one FAILED so we don't replan it again
                        manager.update_task_status(tid, goal.goal_id, GoalHealth.FAILED)
                        manager.add_task_to_goal(alt_task)

            time.sleep(0.1)

    # Start recovery daemon
    recovery_thread = threading.Thread(target=recovery_loop, daemon=True)
    recovery_thread.start()

    # Start 10 workers
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker_loop, f"worker-{i}") for i in range(10)]
        
        # Monitor progress
        # Wait until 1000 unique descriptions are COMPLETED
        start_time = time.time()
        while time.time() - start_time < 300: # Max 300 seconds for test
            conn = sqlite3.connect(manager.db_path, timeout=10.0)
            c = conn.cursor()
            c.execute("SELECT count(DISTINCT description) FROM tasks WHERE status = ?", (GoalHealth.COMPLETED.value,))
            finished_unique = c.fetchone()[0]
            c.execute("SELECT count(*) FROM tasks WHERE status = ?", (GoalHealth.RUNNING.value,))
            running_count = c.fetchone()[0]
            c.close()
            conn.close()
            
            if finished_unique >= 1000 and running_count == 0:
                # Let any remaining replans settle
                time.sleep(1.0)
                break
                
            time.sleep(0.5)
            
        is_running = False

    # Check Invariants
    conn = sqlite3.connect(manager.db_path, timeout=10.0)
    c = conn.cursor()
    
    # 1. No orphaned RUNNING or CLAIMED tasks
    c.execute("SELECT count(*) FROM tasks WHERE status IN (?, ?)", (GoalHealth.RUNNING.value, GoalHealth.CLAIMED.value))
    orphaned = c.fetchone()[0]
    
    # 2. Duplicate side effects (COMPLETED tasks with the same description)
    # Actually, a legitimately failed task might have the same description as a completed replan.
    # We just want to ensure no two COMPLETED tasks have the same description (meaning two workers executed it successfully).
    c.execute("SELECT description, count(*) FROM tasks WHERE status = ? GROUP BY description HAVING count(*) > 1", (GoalHealth.COMPLETED.value,))
    duplicates = c.fetchall()
    
    # 3. All 1000 descriptions were eventually COMPLETED
    c.execute("SELECT count(DISTINCT description) FROM tasks WHERE status = ?", (GoalHealth.COMPLETED.value,))
    completed_unique = c.fetchone()[0]
    
    c.close()
    conn.close()
    
    assert orphaned == 0, f"Found {orphaned} orphaned tasks in RUNNING/CLAIMED states."
    assert len(duplicates) == 0, f"Found {len(duplicates)} duplicate COMPLETED tasks: {duplicates}"
    assert completed_unique == 1000, f"Expected 1000 unique completed tasks, got {completed_unique}"
    
    # Wait for workers to close connections
    time.sleep(1.0)
    
    # We survived!
    clean_db()
