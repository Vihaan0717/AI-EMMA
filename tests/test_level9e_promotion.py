import os
import sys
import pytest
import sqlite3
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from core.candidate_models import CandidateManifest, CandidatePatch
from core.validation_models import ValidationScorecard
from core.promotion_gate import PromotionGate
from core.version_manager import VersionManager, SystemManifest
from core.promotion_ledger import PromotionLedger

@pytest.fixture
def temp_ledger():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture
def dummy_manifest():
    return CandidateManifest(
        candidate_id="CAND-TEST",
        hypothesis_id="HYP-TEST",
        parent_commit="v1.0",
        target_files=["core/dummy.py"],
        modified_files=["core/dummy.py"],
        created_files=[],
        deleted_files=[],
        generator="test",
        analysis_version="1.0",
        status="VALIDATED"
    )

@pytest.fixture
def dummy_scorecard():
    return ValidationScorecard(
        candidate_id="CAND-TEST",
        parent="v1.0",
        status="VALIDATED"
    )

def test_trust_anchor_protection(temp_ledger, dummy_scorecard):
    gate = PromotionGate(temp_ledger)
    manifest = CandidateManifest(
        candidate_id="CAND-EVIL",
        hypothesis_id="HYP-1",
        parent_commit="v1.0",
        target_files=["core/system_limits.py"],
        modified_files=["core/system_limits.py"],
        created_files=[],
        deleted_files=[],
        generator="test",
        analysis_version="1.0",
        status="VALIDATED"
    )
    
    decision = gate.evaluate_candidate(manifest, dummy_scorecard, {"accuracy": 0.9}, {"accuracy": 0.95})
    assert decision == "REJECTED"
    
    # Check ledger recorded reason
    ledger = PromotionLedger(temp_ledger)
    history = ledger.get_history()
    assert len(history) == 1
    assert history[0]["decision_reason"].startswith("TRUST_ANCHOR_VIOLATION")

def test_statistical_gate_inferior(temp_ledger, dummy_manifest, dummy_scorecard):
    gate = PromotionGate(temp_ledger)
    
    # Candidate has worse accuracy
    decision = gate.evaluate_candidate(dummy_manifest, dummy_scorecard, 
                                       champion_metrics={"accuracy": 0.95}, 
                                       challenger_metrics={"accuracy": 0.90})
    assert decision == "REJECTED"
    
    # Candidate has high cost
    decision2 = gate.evaluate_candidate(dummy_manifest, dummy_scorecard, 
                                       champion_metrics={"accuracy": 0.90}, 
                                       challenger_metrics={"accuracy": 0.95, "cost": 10.0})
    assert decision2 == "REJECTED"
    
def test_statistical_gate_superior(temp_ledger, dummy_manifest, dummy_scorecard):
    gate = PromotionGate(temp_ledger)
    decision = gate.evaluate_candidate(dummy_manifest, dummy_scorecard, 
                                       champion_metrics={"accuracy": 0.90}, 
                                       challenger_metrics={
                                           "accuracy": 0.95, 
                                           "cost": 1.0, 
                                           "latency": 0.5, 
                                           "regression_rate": 0.01,
                                           "security_violations": 0
                                       })
    assert decision == "APPROVED"
    
def test_canary_staged_rollout(temp_ledger):
    vm = VersionManager(ledger_path=temp_ledger)
    manifest = SystemManifest(core="1.1.0")
    vm.deploy_manifest(manifest)
    
    assert vm.get_traffic_percentage() == 0.01
    
    # Send 100 successful observations
    for _ in range(100):
        vm.record_canary_observation(failed=False, candidate_id="CAND-TEST")
        
    assert vm.get_traffic_percentage() == 0.05
    
def test_canary_automatic_rollback(temp_ledger, dummy_manifest, dummy_scorecard):
    # First promote a candidate
    gate = PromotionGate(temp_ledger)
    gate.evaluate_candidate(dummy_manifest, dummy_scorecard, 
                            {"accuracy": 0.90}, 
                            {"accuracy": 0.95, "security_violations": 0, "regression_rate": 0.0, "latency": 1.0, "cost": 1.0})
                            
    vm = VersionManager(ledger_path=temp_ledger)
    manifest = SystemManifest(core="1.1.0")
    vm.deploy_manifest(manifest)
    
    assert vm.get_manifest().core == "1.1.0"
    
    # Send 100 failing observations (triggers > 8.7% failure)
    for _ in range(10):
        vm.record_canary_observation(failed=True, candidate_id="CAND-TEST")
    for _ in range(90):
        vm.record_canary_observation(failed=False, candidate_id="CAND-TEST")
        
    # Should have rolled back
    assert vm.get_manifest().core == "1.0.0"
    assert vm.get_traffic_percentage() == 1.0
    
    # Verify ledger was updated
    ledger = PromotionLedger(temp_ledger)
    history = ledger.get_history()
    assert history[0]["rollback_status"].startswith("ROLLED_BACK")
