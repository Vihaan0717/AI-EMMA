"""
Proposal Agent - Safe Code Generation with Docker Sandbox Verification
=======================================================================
Workflow:
  1. LLM generates Python code for the requested feature.
  2. ast.parse validates syntax (fast lightweight check).
  3. Code is executed in an isolated Docker container for runtime safety.
  4. If Docker is unavailable, falls back to a subprocess with a timeout.
  5. Saves verified proposals to the proposals/ directory for human review.
"""

import os
import ast
import datetime
import logging
import subprocess
import tempfile
import shutil

from langchain_ollama import ChatOllama

logger = logging.getLogger("Nexus.ProposalAgent")

DOCKER_AVAILABLE = shutil.which("docker") is not None


class ProposalAgent:
    """
    Generates safe, sandboxed code proposals for human review.
    Never directly modifies core agent files.
    """
    def __init__(self, model_name="llama3.1", ollama_url="http://localhost:11434"):
        self.llm = ChatOllama(model=model_name, base_url=ollama_url)
        self.proposal_dir = "proposals"
        os.makedirs(self.proposal_dir, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Step 1: Syntax Check
    # ------------------------------------------------------------------ #
    def _verify_syntax(self, code: str) -> tuple[bool, str]:
        """Parses the AST to validate Python syntax."""
        try:
            ast.parse(code)
            return True, "Syntax OK"
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"

    # ------------------------------------------------------------------ #
    # Step 2a: Docker Sandbox
    # ------------------------------------------------------------------ #
    def _run_in_docker(self, code: str) -> tuple[bool, str]:
        """Executes code inside a clean Python Docker container."""
        try:
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "--network", "none",         # No network access inside sandbox
                    "--memory", "128m",          # Memory cap
                    "--cpus", "0.5",             # CPU cap
                    "python:3.11-slim",
                    "python", "-c", code
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return True, result.stdout.strip() or "Executed successfully (no output)."
            else:
                return False, f"Runtime Error:\n{result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return False, "Sandbox timeout: code took too long to execute."
        except Exception as e:
            return False, f"Docker execution error: {e}"

    # ------------------------------------------------------------------ #
    # Step 2b: Subprocess Fallback Sandbox
    # ------------------------------------------------------------------ #
    def _run_in_subprocess(self, code: str) -> tuple[bool, str]:
        """Fallback: runs code in a restricted subprocess with timeout."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                tmp_path = f.name

            result = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=20
            )
            os.unlink(tmp_path)
            if result.returncode == 0:
                return True, result.stdout.strip() or "Executed successfully (no output)."
            else:
                return False, f"Runtime Error:\n{result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return False, "Subprocess timeout."
        except Exception as e:
            return False, f"Subprocess error: {e}"

    # ------------------------------------------------------------------ #
    # Public: Generate & Verify
    # ------------------------------------------------------------------ #
    def generate_proposal(self, feature_request: str) -> dict:
        """
        Full pipeline: LLM generation → syntax check → sandbox execution → save proposal.
        Returns a result dict with keys: 'status', 'filename', 'output', 'code'.
        """
        # --- Generate ---
        prompt = (
            f"You are an elite Python developer. Write a clean, functional, standalone Python script "
            f"for this feature: \"{feature_request}\".\n"
            "Output only raw Python code. No markdown. No explanations."
        )
        response = self.llm.invoke(prompt)
        code = response.content.strip()

        # Strip markdown leakage
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()

        # --- Syntax Check ---
        syntax_ok, syntax_msg = self._verify_syntax(code)
        if not syntax_ok:
            logger.error(f"Proposal rejected: {syntax_msg}")
            return {"status": "REJECTED", "reason": syntax_msg, "code": code}

        # --- Sandbox Execution ---
        if DOCKER_AVAILABLE:
            logger.info("Running proposal in Docker sandbox...")
            exec_ok, exec_output = self._run_in_docker(code)
        else:
            logger.info("Docker not found. Running proposal in subprocess sandbox...")
            exec_ok, exec_output = self._run_in_subprocess(code)

        if not exec_ok:
            logger.warning(f"Proposal failed sandbox execution: {exec_output}")
            # Still save it but flag as UNVERIFIED so the human can decide
            status = "UNVERIFIED"
        else:
            status = "VERIFIED"

        # --- Save Proposal ---
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name  = feature_request[:30].replace(" ", "_").replace("/", "_")
        filename   = os.path.join(self.proposal_dir, f"proposal_{safe_name}_{timestamp}.py")

        header = (
            f"# Proposal: {feature_request}\n"
            f"# Status:   {status}\n"
            f"# Sandbox:  {'Docker' if DOCKER_AVAILABLE else 'Subprocess'}\n"
            f"# Output:   {exec_output[:200]}\n"
            f"# Generated: {timestamp}\n\n"
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(header + code)

        logger.info(f"Proposal saved [{status}]: {filename}")
        return {
            "status":   status,
            "filename": filename,
            "output":   exec_output,
            "code":     code
        }
