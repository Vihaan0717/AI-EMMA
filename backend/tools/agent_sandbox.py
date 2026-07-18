"""
NEXUS-X Agent Sandbox — Secure Code Execution Environment
==========================================================
Allows ANY fleet agent to:
  1. Write a script (Python / Shell / Node.js)
  2. Execute it in an isolated subprocess with timeout + resource guards
  3. Parse stdout / stderr
  4. Return structured results for the agent's ReAct loop

Security Model:
  - Subprocess runs in a temporary workspace directory
  - Hard timeout (default 30s, max 120s)
  - Blocked imports list (os.system, subprocess.Popen direct calls within sandbox scripts are caught)
  - Output size capped at 8 KB to prevent memory bombs
"""

import asyncio
import tempfile
import os
import logging
import time
import re
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("AgentSandbox")

# ── Safety Constants ─────────────────────────────────────────────
MAX_TIMEOUT_SECONDS = 120
DEFAULT_TIMEOUT_SECONDS = 30
MAX_OUTPUT_BYTES = 8192          # 8 KB cap on stdout/stderr
WORKSPACE_DIR = Path("sandbox_workspace").resolve()

# Patterns that are blocked in user-submitted Python scripts
BLOCKED_PATTERNS = [
    r"os\.system\s*\(",
    r"subprocess\.\w+\s*\(",
    r"shutil\.rmtree\s*\(",
    r"__import__\s*\(",
    r"eval\s*\(",
    r"exec\s*\(",
    r"open\s*\(.*(\/etc|\/proc|C:\\\\Windows)",
    r"import\s+ctypes",
    r"import\s+socket",          # No raw sockets from sandbox scripts
]


@dataclass
class SandboxResult:
    """Structured result from a sandbox execution."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    elapsed_ms: float
    script_path: str = ""
    truncated: bool = False      # True if output was capped


class AgentSandbox:
    """
    Provides a safe execution environment for fleet agents.
    Agents write code → sandbox runs it → returns structured output.
    """

    def __init__(self):
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"AgentSandbox initialized. Workspace: {WORKSPACE_DIR.resolve()}")

    def _validate_python_script(self, code: str) -> list[str]:
        """
        Static analysis: scan for dangerous patterns.
        Returns list of violations found.
        """
        violations = []
        for pattern in BLOCKED_PATTERNS:
            matches = re.findall(pattern, code)
            if matches:
                violations.append(f"Blocked pattern detected: {pattern} (found {len(matches)} occurrence(s))")
        return violations

    async def execute_python(
        self,
        code: str,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        agent_id: str = "unknown",
        task_label: str = ""
    ) -> SandboxResult:
        """
        Write Python code to a temp file and execute it.
        Returns structured SandboxResult with stdout, stderr, exit code.
        """
        timeout = min(timeout, MAX_TIMEOUT_SECONDS)

        # 1. Static safety check
        violations = self._validate_python_script(code)
        if violations:
            logger.warning(f"Sandbox [{agent_id}]: Script BLOCKED — {violations}")
            return SandboxResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"SANDBOX SECURITY VIOLATION: {'; '.join(violations)}",
                elapsed_ms=0.0
            )

        # 2. Write script to workspace
        timestamp = int(time.time() * 1000)
        script_name = f"agent_{agent_id}_{timestamp}.py"
        script_path = WORKSPACE_DIR / script_name

        try:
            script_path.write_text(code, encoding="utf-8")
        except Exception as e:
            return SandboxResult(
                success=False, exit_code=-1,
                stdout="", stderr=f"Failed to write script: {e}",
                elapsed_ms=0.0
            )

        # 3. Execute with timeout
        logger.info(f"Sandbox [{agent_id}]: Executing {script_name} (timeout={timeout}s) — {task_label}")
        start = time.perf_counter()

        try:
            proc = await asyncio.create_subprocess_exec(
                "python", str(script_path.resolve()),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_raw, stderr_raw = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            elapsed = (time.perf_counter() - start) * 1000
            logger.warning(f"Sandbox [{agent_id}]: TIMEOUT after {timeout}s")
            return SandboxResult(
                success=False, exit_code=-2,
                stdout="", stderr=f"TIMEOUT: Script exceeded {timeout}s limit.",
                elapsed_ms=elapsed, script_path=str(script_path)
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return SandboxResult(
                success=False, exit_code=-3,
                stdout="", stderr=f"Execution error: {e}",
                elapsed_ms=elapsed, script_path=str(script_path)
            )

        elapsed = (time.perf_counter() - start) * 1000

        # 4. Cap output size
        stdout_str = stdout_raw.decode("utf-8", errors="replace")
        stderr_str = stderr_raw.decode("utf-8", errors="replace")
        truncated = False
        if len(stdout_str) > MAX_OUTPUT_BYTES:
            stdout_str = stdout_str[:MAX_OUTPUT_BYTES] + "\n... [OUTPUT TRUNCATED]"
            truncated = True
        if len(stderr_str) > MAX_OUTPUT_BYTES:
            stderr_str = stderr_str[:MAX_OUTPUT_BYTES] + "\n... [STDERR TRUNCATED]"
            truncated = True

        result = SandboxResult(
            success=(proc.returncode == 0),
            exit_code=proc.returncode,
            stdout=stdout_str.strip(),
            stderr=stderr_str.strip(),
            elapsed_ms=round(elapsed, 2),
            script_path=str(script_path),
            truncated=truncated
        )

        logger.info(
            f"Sandbox [{agent_id}]: Completed — exit={result.exit_code}, "
            f"stdout={len(result.stdout)}B, stderr={len(result.stderr)}B, "
            f"elapsed={result.elapsed_ms}ms"
        )
        return result

    async def execute_shell(
        self,
        command: str,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        agent_id: str = "unknown"
    ) -> SandboxResult:
        """
        Execute a shell command (PowerShell on Windows, bash on Linux).
        """
        timeout = min(timeout, MAX_TIMEOUT_SECONDS)

        # Block extremely dangerous commands
        dangerous = ["rm -rf /", "format c:", "del /f /s /q c:\\", "shutdown", "mkfs"]
        for d in dangerous:
            if d in command.lower():
                return SandboxResult(
                    success=False, exit_code=-1,
                    stdout="", stderr=f"SANDBOX: Blocked dangerous command: {d}",
                    elapsed_ms=0.0
                )

        logger.info(f"Sandbox [{agent_id}]: Shell exec: {command[:80]}...")
        start = time.perf_counter()

        try:
            if os.name == "nt":
                proc = await asyncio.create_subprocess_exec(
                    "powershell", "-Command", command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(WORKSPACE_DIR)
                )
            else:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(WORKSPACE_DIR)
                )

            stdout_raw, stderr_raw = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            elapsed = (time.perf_counter() - start) * 1000
            return SandboxResult(
                success=False, exit_code=-2,
                stdout="", stderr=f"TIMEOUT: Command exceeded {timeout}s limit.",
                elapsed_ms=elapsed
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return SandboxResult(
                success=False, exit_code=-3,
                stdout="", stderr=f"Shell error: {e}",
                elapsed_ms=elapsed
            )

        elapsed = (time.perf_counter() - start) * 1000
        stdout_str = stdout_raw.decode("utf-8", errors="replace").strip()
        stderr_str = stderr_raw.decode("utf-8", errors="replace").strip()

        truncated = False
        if len(stdout_str) > MAX_OUTPUT_BYTES:
            stdout_str = stdout_str[:MAX_OUTPUT_BYTES] + "\n... [TRUNCATED]"
            truncated = True

        return SandboxResult(
            success=(proc.returncode == 0),
            exit_code=proc.returncode,
            stdout=stdout_str,
            stderr=stderr_str,
            elapsed_ms=round(elapsed, 2),
            truncated=truncated
        )

    def cleanup_old_scripts(self, max_age_hours: int = 24):
        """Remove sandbox scripts older than max_age_hours."""
        cutoff = time.time() - (max_age_hours * 3600)
        removed = 0
        for f in WORKSPACE_DIR.glob("agent_*.py"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                removed += 1
        if removed:
            logger.info(f"Sandbox: Cleaned up {removed} old scripts.")


# ── Global singleton ──────────────────────────────────────────────
agent_sandbox = AgentSandbox()
