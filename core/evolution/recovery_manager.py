import logging
import time
import sqlite3
from typing import List
from core.goal_manager import GoalManager
from core.goal_models import GoalHealth

logger = logging.getLogger("jarvis.recovery_manager")

class RecoveryManager:
    def __init__(self, manager: GoalManager, heartbeat_timeout_seconds: float = 30.0):
        self.manager = manager
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        
    def scan_and_recover(self) -> int:
        """
        Scans for CLAIMED or RUNNING tasks where the last_heartbeat is older than the timeout.
        Transitions them to INTERRUPTED.
        Returns the number of tasks recovered.
        """
        conn = sqlite3.connect(self.manager.db_path, timeout=10.0)
        c = conn.cursor()
        
        now = time.time()
        timeout_threshold = now - self.heartbeat_timeout_seconds
        
        c.execute('''
            SELECT task_id, goal_id, status FROM tasks 
            WHERE status IN (?, ?) AND last_heartbeat < ?
        ''', (GoalHealth.CLAIMED.value, GoalHealth.RUNNING.value, timeout_threshold))
        
        dead_tasks = c.fetchall()
        conn.close()
        
        recovered_count = 0
        for task_id, goal_id, status in dead_tasks:
            logger.warning(f"RecoveryManager detecting dead task {task_id} (Status: {status}). Marking INTERRUPTED.")
            self.manager.update_task_status(task_id, goal_id, GoalHealth.INTERRUPTED)
            recovered_count += 1
            
        return recovered_count
