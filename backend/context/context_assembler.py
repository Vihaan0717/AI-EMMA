import json
import os
from datetime import datetime
from typing import Any

from core.logger import get_logger
from services.data_layer import data_layer

logger = get_logger("ContextAssembler")


class ContextAssembler:
    """Collects runtime context and converts it into prompt-ready state."""

    def __init__(self, context_path: str = "context/current_state.json"):
        self.context_path = context_path

    def load_runtime_context(self) -> dict[str, Any]:
        default = {
            "active_app": "Unknown",
            "cpu_usage": None,
            "user_idle_seconds": 0,
            "presence_status": "Unknown",
            "battery_level": None,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        if not os.path.exists(self.context_path):
            return default
        try:
            with open(self.context_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {**default, **data}
        except Exception as e:
            logger.error(f"Failed to load runtime context: {e}")
            return default

    def build_prompt_context(self) -> str:
        runtime = self.load_runtime_context()
        preferences = data_layer.preferences.list()
        pending_tasks = data_layer.tasks.list_pending(limit=5)
        recent_interactions = data_layer.feedback.recent_interactions(limit=3)

        lines = [
            f"Current active app: {runtime.get('active_app', 'Unknown')}",
            f"Presence status: {runtime.get('presence_status', 'Unknown')}",
            f"User idle seconds: {runtime.get('user_idle_seconds', 0)}",
        ]

        if runtime.get("battery_level") is not None:
            lines.append(f"Battery level: {runtime['battery_level']}")

        if preferences:
            pref_text = ", ".join(f"{k}={v}" for k, v in sorted(preferences.items()))
            lines.append(f"Stored preferences: {pref_text}")

        if pending_tasks:
            task_text = "; ".join(task["title"] for task in pending_tasks)
            lines.append(f"Pending tasks: {task_text}")

        if recent_interactions:
            interaction_text = " | ".join(item["user_input"] for item in recent_interactions if item.get("user_input"))
            if interaction_text:
                lines.append(f"Recent interactions: {interaction_text}")

        return "\n".join(lines)


context_assembler = ContextAssembler()
