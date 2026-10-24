import logging
from typing import Dict, Any

logger = logging.getLogger("jarvis.system_limits")

# Kill Switches
EMERGENCY_STOP = False
EVOLUTION_MODE = False

class LimitExceededException(Exception):
    """Raised when any hierarchical limit is breached."""
    pass

class SystemLimits:
    MAX_CPU_PERCENT = 80.0
    MAX_RAM_MB = 16000 # E.g., limit total memory usage
    MAX_PROCESSES = 20
    
class TaskLimits:
    MAX_TOKENS = 32000
    MAX_TIME_SECONDS = 300
    MAX_RECURSION = 5
    MAX_TOOL_CALLS = 15

class AgentLimits:
    MAX_DEPTH = 3
    MAX_CALLS_PER_SESSION = 10
    MAX_RUNTIME_SECONDS = 120

class ExperimentLimits:
    MAX_CANDIDATES_PER_EXP = 5
    MAX_API_BUDGET_USD = 10.0
    MIN_SAMPLE_SIZE = 100

class LimitEnforcer:
    def __init__(self):
        self.current_recursion = 0
        self.current_depth = 0
        self.current_processes = 0
        self.current_tokens = 0
        self.tool_calls = 0

    def check_kill_switches(self):
        if EMERGENCY_STOP:
            logger.critical("EMERGENCY_STOP is active. Halting execution.")
            raise LimitExceededException("System killed by EMERGENCY_STOP.")

    def enforce_task_limits(self, token_cost: int = 0):
        self.check_kill_switches()
        self.current_tokens += token_cost
        
        if self.current_recursion >= TaskLimits.MAX_RECURSION:
            raise LimitExceededException(f"TASK LIMIT REACHED: Max recursion ({TaskLimits.MAX_RECURSION})")
            
        if self.tool_calls >= TaskLimits.MAX_TOOL_CALLS:
            raise LimitExceededException(f"TASK LIMIT REACHED: Max tool calls ({TaskLimits.MAX_TOOL_CALLS})")
            
        if self.current_tokens >= TaskLimits.MAX_TOKENS:
            raise LimitExceededException(f"TASK LIMIT REACHED: Max tokens ({TaskLimits.MAX_TOKENS})")

    def enforce_agent_limits(self):
        self.check_kill_switches()
        if self.current_depth >= AgentLimits.MAX_DEPTH:
            raise LimitExceededException(f"AGENT LIMIT REACHED: Max depth ({AgentLimits.MAX_DEPTH})")
            
    def enforce_system_limits(self):
        self.check_kill_switches()
        if self.current_processes >= SystemLimits.MAX_PROCESSES:
            raise LimitExceededException(f"SYSTEM LIMIT REACHED: Max processes ({SystemLimits.MAX_PROCESSES})")

    def enter_agent(self):
        self.current_depth += 1
        self.enforce_agent_limits()
        
    def exit_agent(self):
        self.current_depth = max(0, self.current_depth - 1)
        
    def add_tool_call(self):
        self.tool_calls += 1
        self.enforce_task_limits()
