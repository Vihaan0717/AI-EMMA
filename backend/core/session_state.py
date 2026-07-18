from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SessionState:
    """Normalized state object for one JARVIS interaction turn."""

    channel: str
    user_input: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds"))
    active_app: str = "Unknown"
    presence_status: str = "Unknown"
    user_idle_seconds: int = 0
    memory_context: str = ""
    prompt_context: str = ""
    persona_name: str = "JARVIS"
    persona_style: str = "professional, witty, calm, supportive"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_prompt_payload(self) -> dict[str, Any]:
        return {
            "input": self.user_input,
            "memory": self.memory_context,
            "runtime_context": self.prompt_context,
            "persona_name": self.persona_name,
            "persona_style": self.persona_style,
        }
