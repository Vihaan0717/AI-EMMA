import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from core.candidate_models import CandidateManifest

class DisposableSandbox:
    """
    Context manager that provisions a disposable, isolated environment for testing candidates.
    Copies production files, injects candidate patches, and blocks network via sitecustomize.
    """
    def __init__(self, repo_root: str, candidate_manifest: CandidateManifest):
        self.repo_root = Path(repo_root).resolve()
        self.manifest = candidate_manifest
        self.sandbox_dir: Optional[Path] = None
        
    def __enter__(self) -> str:
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix=f"jarvis_sandbox_{self.manifest.candidate_id}_")
        self.sandbox_dir = Path(temp_dir)
        
        # 1. Copy production files (ignore .git, .venv, .evolution, logs, __pycache__)
        def ignore_patterns(dir_path, contents):
            ignored = []
            for item in contents:
                if item in {".git", ".venv", "venv", ".evolution", "logs", "__pycache__", ".pytest_cache"}:
                    ignored.append(item)
            return ignored
            
        shutil.copytree(self.repo_root, self.sandbox_dir, dirs_exist_ok=True, ignore=ignore_patterns)
        
        # 2. Inject candidate patches from workspace
        workspace_dir = self.repo_root / ".evolution" / "candidates" / self.manifest.candidate_id
        for target in self.manifest.modified_files:
            src = workspace_dir / target
            dst = self.sandbox_dir / target
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                
        # 3. Inject network-blocking and sandbox-enforcing sandbox_hook.py
        hook_path = self.sandbox_dir / "sandbox_hook.py"
        hook_code = f"""
import sys
import os
import ctypes

class SecurityViolation(Exception):
    pass

SANDBOX_ROOT = r"{self.sandbox_dir.resolve()}"
print("HOOK LOADED: " + SANDBOX_ROOT, file=sys.stderr)

def audit_hook(event, args):
    # Block network
    if event.startswith("socket."):
        raise SecurityViolation("NETWORK_DENIED: Socket access is strictly forbidden in candidate validation.")
    
    # Block subprocess creation
    if event in ("os.system", "subprocess.Popen"):
        raise SecurityViolation("SUBPROCESS_DENIED: Candidate attempted to spawn a child process.")
        
    # Restrict file access (allow read, but block write/open if outside sandbox)
    # Actually, to prevent reading trust anchors, we block ALL open outside sandbox except python stdlib
    if event == "open":
        path = args[0]
        if isinstance(path, str):
            try:
                repo_root = r"{self.repo_root.resolve()}"
                abs_path = os.path.realpath(path)
                print(f"HOOK OPEN: {{abs_path}}", file=sys.stderr)
                # If they try to touch anything in OP repo that isn't inside the sandbox temp dir
                if abs_path.lower().startswith(repo_root.lower()) and not abs_path.lower().startswith(SANDBOX_ROOT.lower()):
                    raise SecurityViolation(f"ESCAPE_DENIED: Attempted to access production file: {{path}}")
            except SecurityViolation:
                raise
            except Exception as e:
                print(f"HOOK ERROR: {{e}}", file=sys.stderr)

sys.addaudithook(audit_hook)
"""
        with open(hook_path, "w", encoding="utf-8") as f:
            f.write(hook_code)
            
        return str(self.sandbox_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Always destroy the sandbox on exit
        if self.sandbox_dir and self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)
