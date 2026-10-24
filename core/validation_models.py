from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ValidationScorecard:
    candidate_id: str
    parent: str
    status: str # VALIDATED, TIMEOUT, RESOURCE_LIMIT, NETWORK_DENIED, REJECTED, REGRESSION_FAILED
    tests: Dict[str, str] = field(default_factory=dict) # e.g. {"unit": "PASS", "regression": "FAIL"}
    performance: Dict[str, float] = field(default_factory=dict) # e.g. {"latency_delta": -0.21}
    resource_limits: Dict[str, str] = field(default_factory=dict) # e.g. {"memory": "PASS"}
    
    # Resource Ledger
    runtime_sec: float = 0.0
    peak_ram_mb: float = 0.0
    cpu_time_sec: float = 0.0
    processes_created: int = 0
    peak_processes: int = 0
    output_bytes: int = 0
    files_touched: int = 0
    network_attempts: int = 0
    exit_code: int = -1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "parent": self.parent,
            "status": self.status,
            "tests": self.tests,
            "performance": self.performance,
            "resource_limits": self.resource_limits,
            "ledger": {
                "runtime_sec": self.runtime_sec,
                "peak_ram_mb": self.peak_ram_mb,
                "cpu_time_sec": self.cpu_time_sec,
                "processes_created": self.processes_created,
                "peak_processes": self.peak_processes,
                "output_bytes": self.output_bytes,
                "files_touched": self.files_touched,
                "network_attempts": self.network_attempts,
                "exit_code": self.exit_code
            }
        }
        
    def __str__(self) -> str:
        passed = sum(1 for v in self.tests.values() if v == "PASS")
        failed = sum(1 for v in self.tests.values() if v == "FAIL")
        
        return f"""Candidate: {self.candidate_id}

Runtime:             {self.runtime_sec:.2f} s
Peak RAM:            {self.peak_ram_mb:.0f} MB
CPU time:            {self.cpu_time_sec:.2f} s
Processes created:   {self.processes_created}
Peak processes:      {self.peak_processes}
Output:              {self.output_bytes / 1024:.0f} KB
Files touched:       {self.files_touched}
Network attempts:    {self.network_attempts}
Exit code:           {self.exit_code}

Tests:
    passed:           {passed}
    failed:           {failed}

Result:
    {self.status}
"""
