"""
NEXUS-X Goal Manager
======================
Handles persistent storage and CRUD operations for:
1. Long-term goals (continuous open-ended research)
2. Scheduled tasks (specific actions queued for a specific time)

State is persisted to memory/agent_goals.json.
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid

logger = logging.getLogger("GoalManager")

class GoalManager:
    def __init__(self):
        self.db_path = Path("memory/agent_goals.json")
        self.max_goals_per_agent = 5
        self._state = {
            "goals": {},        # agent_id -> list of goal dicts
            "scheduled": []     # list of scheduled task dicts
        }
        self._load()

    def _load(self):
        """Load state from disk."""
        if self.db_path.exists():
            try:
                data = json.loads(self.db_path.read_text(encoding="utf-8"))
                self._state["goals"] = data.get("goals", {})
                self._state["scheduled"] = data.get("scheduled", [])
                logger.info(f"Loaded {len(self._state['scheduled'])} scheduled tasks.")
            except Exception as e:
                logger.error(f"Failed to load agent goals: {e}")

    def _save(self):
        """Save state to disk."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.db_path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to save agent goals: {e}")

    # ── Long-term Goals ──────────────────────────────────────────────
    
    def add_goal(self, agent_id: str, description: str) -> Dict[str, Any]:
        agent_id = agent_id.lower()
        if agent_id not in self._state["goals"]:
            self._state["goals"][agent_id] = []
            
        if len(self._state["goals"][agent_id]) >= self.max_goals_per_agent:
            return {"success": False, "error": f"Agent {agent_id} reached max goals limit ({self.max_goals_per_agent})."}
            
        goal_id = str(uuid.uuid4())[:8]
        goal = {
            "id": goal_id,
            "description": description,
            "status": "active",
            "created_at": time.time()
        }
        self._state["goals"][agent_id].append(goal)
        self._save()
        logger.info(f"Goal added for {agent_id}: {description[:50]}...")
        return {"success": True, "goal_id": goal_id}

    def complete_goal(self, agent_id: str, goal_id: str) -> bool:
        agent_id = agent_id.lower()
        if agent_id in self._state["goals"]:
            for goal in self._state["goals"][agent_id]:
                if goal["id"] == goal_id:
                    goal["status"] = "completed"
                    goal["completed_at"] = time.time()
                    self._save()
                    return True
        return False

    def get_active_goals(self, agent_id: str) -> List[Dict[str, Any]]:
        agent_id = agent_id.lower()
        return [g for g in self._state["goals"].get(agent_id, []) if g["status"] == "active"]

    # ── Scheduled Tasks ──────────────────────────────────────────────

    def schedule_task(self, target_agent: str, task: str, run_at_timestamp: float) -> Dict[str, Any]:
        """Schedule a specific task to run at a future timestamp."""
        task_id = str(uuid.uuid4())[:8]
        scheduled_item = {
            "id": task_id,
            "target_agent": target_agent.lower(),
            "task": task,
            "run_at": run_at_timestamp,
            "status": "pending",
            "created_at": time.time()
        }
        self._state["scheduled"].append(scheduled_item)
        self._save()
        logger.info(f"Task scheduled for {target_agent} at {run_at_timestamp}: {task[:50]}...")
        return {"success": True, "task_id": task_id}

    def get_due_tasks(self) -> List[Dict[str, Any]]:
        """Return all pending tasks where run_at <= current time."""
        now = time.time()
        due_tasks = []
        for t in self._state["scheduled"]:
            if t["status"] == "pending" and t["run_at"] <= now:
                due_tasks.append(t)
        return due_tasks

    def mark_task_complete(self, task_id: str, result: str = ""):
        """Mark a scheduled task as complete."""
        for t in self._state["scheduled"]:
            if t["id"] == task_id:
                t["status"] = "completed"
                t["result"] = result
                t["completed_at"] = time.time()
                break
        self._save()

# Global Singleton
goal_manager = GoalManager()
