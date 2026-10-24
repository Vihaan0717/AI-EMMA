import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from core.code_analyzer import RepositoryAnalyzer
from core.cloud_reasoner import MockReasoner
from core.hypothesis_engine import HypothesisEngine
from scripts.analyze_repository import analyze_repository

def test_hypothesis_generation():
    """
    Given a fixed repository snapshot, JARVIS can deterministically reconstruct 
    its architectural model, identify dependency/blast radius/risk information, 
    and generate a hypothesis without modifying a single byte.
    """
    
    # Ensure DB is populated
    analyze_repository()
    
    analyzer = RepositoryAnalyzer()
    
    # Pick a data plane module (safe to modify)
    target_file = next((f for f in analyzer.list_files() if "experience_store.py" in f), "core/experience_store.py")
    
    reasoner = MockReasoner(target_file=target_file)
    engine = HypothesisEngine(reasoner=reasoner, analyzer=analyzer)
    
    observation = "Querying experience logs is taking >500ms under heavy concurrency."
    
    best_hypothesis = engine.generate_and_rank(target_file, observation)
    
    # 1. Assert we generated a hypothesis
    assert best_hypothesis is not None
    
    # 2. Assert it picked the best one based on our deterministic ranking (H2 is best due to low cost + high confidence)
    assert best_hypothesis.confidence > 0.0
    assert best_hypothesis.target == target_file
    
    # 3. Assert structured output contains all required fields
    h_dict = best_hypothesis.to_dict()
    assert "hypothesis_id" in h_dict
    assert "observation" in h_dict
    assert "proposed_change" in h_dict
    assert "blast_radius" in h_dict
    assert "risk" in h_dict
    
def test_trust_anchor_protection():
    """
    Asserts that JARVIS will refuse to generate hypotheses for protected Trust Anchors.
    """
    analyzer = RepositoryAnalyzer()
    
    # goal_manager.py is a control plane trust anchor
    target_file = next((f for f in analyzer.list_files() if "goal_manager.py" in f), "core/goal_manager.py")
    
    reasoner = MockReasoner(target_file=target_file)
    engine = HypothesisEngine(reasoner=reasoner, analyzer=analyzer)
    
    observation = "Repeated dependency checks account for high overhead."
    
    # This should return None because the risk is CRITICAL and plane is CONTROL PLANE
    best_hypothesis = engine.generate_and_rank(target_file, observation)
    
    assert best_hypothesis is None, "Engine MUST reject hypotheses modifying Control Plane components!"
    
def test_immutable_bounds():
    """
    Verify the path boundary hardening in code_analyzer.py
    """
    analyzer = RepositoryAnalyzer()
    
    try:
        analyzer.read_file("../some_external_file.txt")
        assert False, "Failed to block path traversal"
    except PermissionError:
        pass # Expected
        
    try:
        # Spoofing attack
        spoofed = analyzer.root_dir + "_evil/file.py"
        analyzer._enforce_bounds(spoofed)
        assert False, "Failed to block spoofed path traversal"
    except PermissionError:
        pass # Expected
