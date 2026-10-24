import os
import sys
import shutil
import pytest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from core.hypothesis_models import Hypothesis
from core.candidate_models import CandidatePatch
from core.candidate_generator import CandidateGenerator, CandidateWorkspace, DiffGate

@pytest.fixture(scope="module")
def repo_root():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def mock_hypothesis():
    return Hypothesis(
        goal_id="GOAL-31",
        failure_id="FAIL-882",
        hypothesis_id="HYP-017",
        target="core/experience_store.py",
        observation="Repeated database reads.",
        proposed_change="Cache reads.",
        expected_benefit="Lower latency.",
        confidence=0.9,
        risk="LOW",
        blast_radius=5,
        required_tests=[],
        estimated_cost=10.0,
        evidence="Logs show latency."
    )

def test_candidate_workspace_isolation(repo_root, mock_hypothesis):
    """
    Test that a valid candidate is written into .evolution/candidates/<id>
    and not to the production repository, and that a manifest is generated.
    """
    generator = CandidateGenerator(root_dir=repo_root)
    patches = [CandidatePatch(relative_path="core/experience_store.py", content="# MOCK CACHE ADDED")]
    
    manifest = generator.generate_candidate(mock_hypothesis, patches)
    
    workspace_dir = Path(repo_root) / ".evolution" / "candidates" / manifest.candidate_id
    
    # 1. Workspace was created
    assert workspace_dir.exists()
    
    # 2. Patch was written to workspace
    patch_path = workspace_dir / "core" / "experience_store.py"
    assert patch_path.exists()
    
    with open(patch_path, "r") as f:
        assert f.read() == "# MOCK CACHE ADDED"
        
    # 3. Manifest was written
    manifest_path = workspace_dir / "candidate_manifest.json"
    assert manifest_path.exists()
    
    # Cleanup
    shutil.rmtree(workspace_dir)

def test_malicious_generated_path(repo_root):
    """
    Test that the workspace blocks path traversal attempts.
    """
    with CandidateWorkspace(repo_root, "CAND-EVIL") as workspace:
        # Attempt traversal outside workspace
        with pytest.raises(PermissionError, match="escapes workspace root"):
            workspace.write_candidate_file("../../core/system_limits.py", "malicious payload")
            
        # Attempt absolute path spoofing (windows format or posix depending on env)
        with pytest.raises(PermissionError):
            absolute_path = os.path.abspath(os.path.join(repo_root, "core/system_limits.py"))
            workspace.write_candidate_file(absolute_path, "malicious payload")

def test_unexpected_file_rejection(repo_root, mock_hypothesis):
    """
    Test DiffGate rejecting candidates that modify files outside the hypothesis scope.
    """
    generator = CandidateGenerator(root_dir=repo_root)
    
    # Hypothesis target is core/experience_store.py, but patch tries to touch nexus_master.py
    patches = [CandidatePatch(relative_path="core/nexus_master.py", content="invalid")]
    
    with pytest.raises(ValueError, match="modified unexpected file"):
        generator.generate_candidate(mock_hypothesis, patches)

def test_control_plane_rejection(repo_root):
    """
    Test DiffGate rejecting attempts to modify Control Plane / Trust Anchors.
    """
    # Create hypothesis targeting a control plane module
    hyp = Hypothesis(
        goal_id="G1", failure_id="F1", hypothesis_id="H1",
        target="core/goal_manager.py", observation="", proposed_change="", 
        expected_benefit="", confidence=1.0, risk="CRITICAL", blast_radius=1, 
        required_tests=[], estimated_cost=1.0, evidence=""
    )
    
    generator = CandidateGenerator(root_dir=repo_root)
    patches = [CandidatePatch(relative_path="core/goal_manager.py", content="# modified trust anchor")]
    
    with pytest.raises(ValueError, match="Attempted to modify Trust Anchor"):
        generator.generate_candidate(hyp, patches)
