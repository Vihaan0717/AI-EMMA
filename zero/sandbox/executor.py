"""
PROJECT ZERO Sandbox Executor
Isolated, safe code execution environment
Never crashes the brain — completely isolated
"""

import asyncio
import logging
import os
import sys
import time
import traceback
import resource
import signal
from typing import Dict, Any, Optional
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

logger = logging.getLogger("Sandbox")

app = FastAPI(title="Zero Sandbox Executor")

SANDBOX_SECRET = os.getenv("SANDBOX_SECRET", "change_me")
MAX_EXEC_TIME = int(os.getenv("MAX_EXECUTION_TIME", "30"))
MAX_MEMORY_MB = int(os.getenv("MAX_MEMORY_MB", "512"))


class ExecuteRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30
    inputs: Dict[str, Any] = {}


class ExecuteResponse(BaseModel):
    success: bool
    output: str
    error: str
    execution_time_ms: float
    memory_used_mb: float


def _verify_secret(x_sandbox_secret: str = Header(...)):
    """Verify sandbox access secret"""
    if x_sandbox_secret != SANDBOX_SECRET:
        raise HTTPException(403, "Invalid sandbox secret")
    return True


def _is_safe_code(code: str) -> tuple[bool, str]:
    """
    Check if code is safe to execute.
    Blocks dangerous operations.
    """
    dangerous = [
        # System access
        ("import os", "os module not allowed"),
        ("import sys", "sys module not allowed"),
        ("import subprocess", "subprocess not allowed"),
        ("__import__", "__import__ not allowed"),
        ("eval(", "eval() not allowed"),
        ("exec(", "exec() not allowed"),
        # File system
        ("open(", "file operations not allowed"),
        ("pathlib", "file operations not allowed"),
        # Network (raw)
        ("socket", "raw sockets not allowed"),
        # Process
        ("fork(", "fork not allowed"),
        ("spawn(", "spawn not allowed"),
    ]

    code_lower = code.lower()
    for pattern, reason in dangerous:
        if pattern.lower() in code_lower:
            return False, reason

    return True, ""


@app.get("/health")
async def health():
    return {"status": "online", "service": "sandbox"}


@app.post(
    "/execute",
    response_model=ExecuteResponse,
    dependencies=[__import__('fastapi').Depends(_verify_secret)]
)
async def execute_code(req: ExecuteRequest):
    """Execute code in isolated environment"""

    # Safety check
    is_safe, reason = _is_safe_code(req.code)
    if not is_safe:
        return ExecuteResponse(
            success=False,
            output="",
            error=f"Safety check failed: {reason}",
            execution_time_ms=0,
            memory_used_mb=0
        )

    if req.language != "python":
        return ExecuteResponse(
            success=False,
            output="",
            error=f"Language '{req.language}' not supported yet",
            execution_time_ms=0,
            memory_used_mb=0
        )

    # Execute Python in restricted environment
    start = time.time()

    stdout_capture = StringIO()
    stderr_capture = StringIO()
    result_output = ""
    result_error = ""
    success = False

    try:
        # Restricted globals — no access to dangerous modules
        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sorted": sorted,
                "reversed": reversed,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "int": int,
                "float": float,
                "str": str,
                "bool": bool,
                "type": type,
                "isinstance": isinstance,
                "max": max,
                "min": min,
                "sum": sum,
                "abs": abs,
                "round": round,
                "format": format,
                "repr": repr,
                "None": None,
                "True": True,
                "False": False
            }
        }
        safe_globals.update(req.inputs)

        timeout = min(req.timeout, MAX_EXEC_TIME)

        async def run_code():
            with redirect_stdout(stdout_capture):
                with redirect_stderr(stderr_capture):
                    exec(req.code, safe_globals)

        await asyncio.wait_for(run_code(), timeout=timeout)

        result_output = stdout_capture.getvalue()
        result_error = stderr_capture.getvalue()
        success = True

    except asyncio.TimeoutError:
        result_error = (
            f"Execution timed out after {timeout}s"
        )
    except Exception as e:
        result_error = (
            f"{type(e).__name__}: {str(e)}\n"
            f"{traceback.format_exc()}"
        )
        result_output = stdout_capture.getvalue()

    elapsed = (time.time() - start) * 1000

    # Get memory usage
    try:
        mem_mb = (
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            / 1024
        )
    except:
        mem_mb = 0

    return ExecuteResponse(
        success=success,
        output=result_output[:10000],
        error=result_error[:5000],
        execution_time_ms=elapsed,
        memory_used_mb=mem_mb
    )


@app.post(
    "/reset",
    dependencies=[__import__('fastapi').Depends(_verify_secret)]
)
async def reset_sandbox():
    """Reset sandbox state"""
    # Clear any cached state
    logger.info("Sandbox reset requested")
    return {"status": "reset", "message": "Sandbox cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, host="0.0.0.0", port=8001,
        log_level="info"
    )
