from dataclasses import dataclass, field
from typing import Dict, List, Optional
from core.agent_result import AgentResult

@dataclass
class OrchestrationState:
    request: str
    intent: Optional[str] = None
    complexity: Optional[str] = None
    requires_tools: bool = False
    needs_clarification: bool = False
    selected_tools: List[str] = field(default_factory=list)
    selected_agents: List[str] = field(default_factory=list)
    tool_arguments: Dict[str, Dict] = field(default_factory=dict)
    execution_results: Dict[str, AgentResult] = field(default_factory=dict)
    validation_results: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    final_answer: Optional[str] = None
