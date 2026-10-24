import json
from dataclasses import dataclass, field
from typing import List

@dataclass
class AgentResult:
    status: str = "success"
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    answer: str = ""
    needs_verification: bool = False
    errors: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        """Returns the JSON string representation of the result."""
        from dataclasses import asdict
        return json.dumps(asdict(self))
