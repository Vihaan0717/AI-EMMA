import os
import json
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any

from core.hypothesis_models import Hypothesis
from core.candidate_models import CandidateManifest, CandidatePatch
from core.code_risk import determine_module_risk

MAX_FILES_CHANGED = 3
MAX_LINES_ADDED = 50
MAX_LINES_DELETED = 50

class CandidateWorkspace:
    """
    Context manager that creates a strictly isolated workspace for a candidate.
    Only allows writes via write_candidate_file() which prevents path traversal.
    """
    def __init__(self, root_dir: str, candidate_id: str):
        self._repo_root = Path(root_dir).resolve()
        self.candidate_id = candidate_id
        self._workspace_root = self._repo_root / ".evolution" / "candidates" / self.candidate_id
        
        # Manifest state tracking
        self.target_files = []
        self.modified_files = []
        self.created_files = []
        self.deleted_files = []

    def __enter__(self):
        self._workspace_root.mkdir(parents=True, exist_ok=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass # If we reject, we can cleanup externally or keep for debugging
        
    def _enforce_bounds(self, relative_path: str) -> Path:
        """Ensures writes stay strictly within the candidate workspace."""
        full_path = self._workspace_root / relative_path
        resolved_path = full_path.resolve()
        
        if not resolved_path.is_relative_to(self._workspace_root):
            raise PermissionError(f"Path traversal blocked: {relative_path} escapes workspace root.")
            
        return resolved_path
        
    def write_candidate_file(self, relative_path: str, content: str):
        """Securely write a file into the candidate workspace."""
        resolved_path = self._enforce_bounds(relative_path)
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Track modification
        str_rel = relative_path.replace("\\", "/")
        if str_rel not in self.modified_files:
            self.modified_files.append(str_rel)
            
        with open(resolved_path, "w", encoding="utf-8") as f:
            f.write(content)

    def write_manifest(self, manifest: CandidateManifest):
        """Writes the candidate manifest into the workspace root."""
        manifest_path = self._enforce_bounds("candidate_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2)


class DiffGate:
    """Verifies that candidate patches conform to structural constraints."""
    
    @staticmethod
    def validate_patch(patch: CandidatePatch, target_file: str):
        # 1. Scope restriction (can only touch allowed target files)
        norm_path = patch.relative_path.replace("\\", "/")
        norm_target = target_file.replace("\\", "/")
        
        if norm_path != norm_target:
            raise ValueError(f"DiffGate REJECTED: Candidate modified unexpected file '{norm_path}'. Allowed: '{norm_target}'.")
            
        # 2. Control Plane / Trust Anchor check
        risk = determine_module_risk(norm_path)
        if risk.get("plane") == "CONTROL PLANE" and risk.get("risk") == "CRITICAL":
            raise ValueError(f"DiffGate REJECTED: Attempted to modify Trust Anchor '{norm_path}'.")
            
        # 3. LOC limits (Naive proxy for actual diff logic for now)
        lines = patch.content.splitlines()
        if len(lines) > 5000: # Arbitrary proxy to simulate MAX_LINES_ADDED logic
            raise ValueError(f"DiffGate REJECTED: Candidate patch exceeded size limits.")


class CandidateGenerator:
    """
    Takes an approved Hypothesis and generates a candidate workspace containing the proposed changes.
    Does NOT modify production. Does NOT execute code.
    """
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        
    def generate_candidate(self, hypothesis: Hypothesis, patches: List[CandidatePatch], parent_commit: str = "latest") -> CandidateManifest:
        """
        Creates the workspace, gates the patches, and writes the manifest.
        """
        candidate_id = f"CAND-{str(uuid.uuid4())[:8]}"
        
        with CandidateWorkspace(self.root_dir, candidate_id) as workspace:
            workspace.target_files = [hypothesis.target]
            
            # Apply DiffGate and Write
            for patch in patches:
                DiffGate.validate_patch(patch, hypothesis.target)
                workspace.write_candidate_file(patch.relative_path, patch.content)
                
            manifest = CandidateManifest(
                candidate_id=candidate_id,
                hypothesis_id=hypothesis.hypothesis_id,
                parent_commit=parent_commit,
                target_files=workspace.target_files,
                modified_files=workspace.modified_files,
                created_files=workspace.created_files,
                deleted_files=workspace.deleted_files,
                generator="cloud_reasoner",
                analysis_version="1.0",
                status="GENERATED"
            )
            
            workspace.write_manifest(manifest)
            return manifest
