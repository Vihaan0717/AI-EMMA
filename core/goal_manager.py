import sqlite3
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from core.goal_models import Goal, Task, GoalHealth, AutonomyBudget, GoalMetrics, CompletionCriteria, Evidence

logger = logging.getLogger("jarvis.goal_manager")

class GoalManager:
    def __init__(self, db_path: str = "logs/goals.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self.consecutive_failures = {}

    def _init_db(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                goal_id TEXT PRIMARY KEY,
                parent_goal_id TEXT,
                description TEXT,
                status TEXT,
                progress REAL,
                budget_json TEXT,
                completion_criteria_json TEXT,
                evidence_json TEXT,
                created_at REAL,
                updated_at REAL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                goal_id TEXT,
                description TEXT,
                status TEXT,
                metrics_json TEXT,
                progress REAL,
                dependencies_json TEXT,
                worker_id TEXT,
                last_heartbeat REAL,
                idempotency_key TEXT,
                completion_criteria_json TEXT,
                evidence_json TEXT,
                created_at REAL,
                updated_at REAL,
                FOREIGN KEY(goal_id) REFERENCES goals(goal_id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_goal(self, goal: Goal):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO goals 
            (goal_id, parent_goal_id, description, status, progress, budget_json, 
             completion_criteria_json, evidence_json, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (goal.goal_id, goal.parent_goal_id, goal.description, goal.status.value, goal.progress, 
              goal.budget.model_dump_json(), 
              goal.completion_criteria.model_dump_json() if goal.completion_criteria else None,
              goal.evidence.model_dump_json() if goal.evidence else None,
              goal.created_at, goal.updated_at))
        
        for task in goal.tasks:
            self._add_task(c, task)
            
        conn.commit()
        conn.close()

    def _add_task(self, cursor, task: Task):
        cursor.execute('''
            INSERT OR REPLACE INTO tasks
            (task_id, goal_id, description, status, metrics_json, progress, dependencies_json, 
             worker_id, last_heartbeat, idempotency_key, completion_criteria_json, evidence_json, 
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task.task_id, task.goal_id, task.description, task.status.value, 
              task.metrics.model_dump_json(), task.progress, json.dumps(task.dependencies),
              task.worker_id, task.last_heartbeat, task.idempotency_key,
              task.completion_criteria.model_dump_json() if task.completion_criteria else None,
              task.evidence.model_dump_json() if task.evidence else None,
              task.created_at, task.updated_at))

    def add_task_to_goal(self, task: Task):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        c = conn.cursor()
        self._add_task(c, task)
        conn.commit()
        conn.close()

    def update_task_status(self, task_id: str, goal_id: str, status: GoalHealth, progress: float = None, expected_status: GoalHealth = None) -> bool:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        c = conn.cursor()
        updated_at = time.time()
        
        updates = ["status = ?", "updated_at = ?"]
        params = [status.value, updated_at]
        
        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)
            
        params.append(task_id)
        
        where_clause = "WHERE task_id = ?"
        if expected_status:
            where_clause += " AND status = ?"
            params.append(expected_status.value)
            
        c.execute(f'UPDATE tasks SET {", ".join(updates)} {where_clause}', tuple(params))
        success = c.rowcount > 0
        conn.commit()
        conn.close()
        
        if expected_status and not success:
            return False
        
        # Track consecutive failures for the AT_RISK rule
        if status in [GoalHealth.FAILED, GoalHealth.TIMEOUT, GoalHealth.INTERRUPTED]:
            self.consecutive_failures[goal_id] = self.consecutive_failures.get(goal_id, 0) + 1
            if self.consecutive_failures[goal_id] >= 3:
                self.update_goal_status(goal_id, GoalHealth.AT_RISK)
                logger.warning(f"Goal {goal_id} marked AT_RISK (3 consecutive task failures)")
        elif status == GoalHealth.COMPLETED:
            self.consecutive_failures[goal_id] = 0
            
        return success

    def update_goal_status(self, goal_id: str, status: GoalHealth, progress: float = None):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        c = conn.cursor()
        updated_at = time.time()
        
        updates = ["status = ?", "updated_at = ?"]
        params = [status.value, updated_at]
        
        if progress is not None:
            updates.append("progress = ?")
            params.append(progress)
            
        params.append(goal_id)
        c.execute(f'UPDATE goals SET {", ".join(updates)} WHERE goal_id = ?', tuple(params))
        conn.commit()
        conn.close()

    def update_heartbeat(self, task_id: str):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        c = conn.cursor()
        c.execute('UPDATE tasks SET last_heartbeat = ?, updated_at = ? WHERE task_id = ?', 
                  (time.time(), time.time(), task_id))
        conn.commit()
        conn.close()

    def get_pending_tasks(self) -> List[Task]:
        """Returns tasks that are PENDING."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        c = conn.cursor()
        c.execute('SELECT task_id, goal_id, description, status, metrics_json, progress, dependencies_json, worker_id, last_heartbeat, idempotency_key, completion_criteria_json, evidence_json, created_at, updated_at FROM tasks WHERE status = ?', (GoalHealth.PENDING.value,))
        rows = c.fetchall()
        conn.close()
        
        tasks = []
        for r in rows:
            task = Task(
                task_id=r[0],
                goal_id=r[1],
                description=r[2],
                status=GoalHealth(r[3]),
                metrics=GoalMetrics.model_validate_json(r[4]),
                progress=r[5],
                dependencies=json.loads(r[6]),
                worker_id=r[7],
                last_heartbeat=r[8],
                idempotency_key=r[9],
                completion_criteria=CompletionCriteria.model_validate_json(r[10]) if r[10] else None,
                evidence=Evidence.model_validate_json(r[11]) if r[11] else None,
                created_at=r[12],
                updated_at=r[13]
            )
            tasks.append(task)
        return tasks

    def claim_task(self, task_id: str, worker_id: str) -> bool:
        """Atomic transaction to claim a task. Prevents duplicates."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT status FROM tasks WHERE task_id = ?', (task_id,))
        row = c.fetchone()
        if not row or row[0] != GoalHealth.PENDING.value:
            conn.close()
            return False # Already claimed or not pending
            
        now = time.time()
        c.execute('''
            UPDATE tasks 
            SET status = ?, worker_id = ?, last_heartbeat = ?, updated_at = ?
            WHERE task_id = ? AND status = ?
        ''', (GoalHealth.CLAIMED.value, worker_id, now, now, task_id, GoalHealth.PENDING.value))
        
        success = c.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_task_status(self, task_id: str) -> Optional[GoalHealth]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT status FROM tasks WHERE task_id = ?', (task_id,))
        row = c.fetchone()
        conn.close()
        return GoalHealth(row[0]) if row else None
