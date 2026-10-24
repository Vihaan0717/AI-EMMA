import os
import sys
import shutil
import pytest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from core.candidate_models import CandidateManifest, CandidatePatch
from core.candidate_generator import CandidateGenerator, CandidateWorkspace
from core.hypothesis_models import Hypothesis
from core.validation_engine import ValidationEngine

@pytest.fixture(scope="module")
def repo_root():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def mock_hypothesis():
    return Hypothesis(
        goal_id="G1", failure_id="F1", hypothesis_id="H1", target="dummy_test.py",
        observation="", proposed_change="", expected_benefit="",
        confidence=1.0, risk="LOW", blast_radius=1, required_tests=[],
        estimated_cost=1.0, evidence=""
    )

def _generate_candidate(repo_root, hyp, code) -> CandidateManifest:
    generator = CandidateGenerator(root_dir=repo_root)
    patches = [CandidatePatch(relative_path="dummy_test.py", content=code)]
    return generator.generate_candidate(hyp, patches)

def test_candidate_a_valid(repo_root, mock_hypothesis):
    """Candidate A: valid optimization -> VALIDATED"""
    code = "print('Optimization successful')"
    manifest = _generate_candidate(repo_root, mock_hypothesis, code)
    
    engine = ValidationEngine(repo_root=repo_root)
    scorecard = engine.validate_candidate(manifest)
    assert scorecard.status == "VALIDATED"

def test_candidate_b_infinite_loop(repo_root, mock_hypothesis):
    """Candidate B: infinite loop -> TIMEOUT"""
    code = "import time\nwhile True:\n    time.sleep(0.1)"
    manifest = _generate_candidate(repo_root, mock_hypothesis, code)
    
    engine = ValidationEngine(repo_root=repo_root)
    
    scorecard = engine.validate_candidate(manifest)
    assert scorecard.status == "TIMEOUT"

def test_candidate_c_memory_leak(repo_root, mock_hypothesis):
    """Candidate C: excessive memory allocation -> RESOURCE_LIMIT"""
    # Our engine simulates detecting memory limit by looking for MemoryError
    code = "print('allocate_excessive_memory')\nraise MemoryError('Out of memory')"
    manifest = _generate_candidate(repo_root, mock_hypothesis, code)
    
    engine = ValidationEngine(repo_root=repo_root)
    scorecard = engine.validate_candidate(manifest)
    assert scorecard.status == "RESOURCE_LIMIT"

def test_candidate_d_network_access(repo_root, mock_hypothesis):
    """Candidate D: attempted network access -> NETWORK_DENIED"""
    code = "import socket\ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)"
    manifest = _generate_candidate(repo_root, mock_hypothesis, code)
    
    engine = ValidationEngine(repo_root=repo_root)
    scorecard = engine.validate_candidate(manifest)
    assert scorecard.status == "NETWORK_DENIED"

def test_candidate_e_control_plane(repo_root):
    """Candidate E: attempted control-plane modification -> REJECTED"""
    hyp = Hypothesis(
        goal_id="G1", failure_id="F1", hypothesis_id="H2", target="core/system_limits.py",
        observation="", proposed_change="", expected_benefit="",
        confidence=1.0, risk="CRITICAL", blast_radius=1, required_tests=[],
        estimated_cost=1.0, evidence=""
    )
    generator = CandidateGenerator(root_dir=repo_root)
    patches = [CandidatePatch(relative_path="core/system_limits.py", content="# modified")]
    
    with pytest.raises(ValueError, match="Attempted to modify Trust Anchor"):
        generator.generate_candidate(hyp, patches)
        
def test_candidate_f_regression(repo_root, mock_hypothesis):
    """Candidate F: regression-inducing change -> REGRESSION_FAILED"""
    code = "assert False, 'Regression test failed'"
    manifest = _generate_candidate(repo_root, mock_hypothesis, code)
    
    engine = ValidationEngine(repo_root=repo_root)
    scorecard = engine.validate_candidate(manifest)
    assert scorecard.status == "REGRESSION_FAILED"
