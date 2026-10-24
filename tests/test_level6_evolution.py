import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.system_limits import LimitEnforcer, LimitExceededException, TaskLimits
from core.version_manager import VersionManager, SystemManifest
from evolution_lab.reasoner import MockReasoner
from evolution_lab.failure_analyzer import FailureAnalyzer, FailurePattern
from evolution_lab.experiment_manager import ExperimentManager, CandidateConfiguration
from evolution_lab.sandbox import SandboxLab, Scorecard
from evolution_lab.promotion_gate import PromotionGate

@pytest.fixture(autouse=True)
def clean_level6_dbs():
    db_paths = ["logs/test_evo.db"]
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)
    yield
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)

def test_hierarchical_limits():
    enforcer = LimitEnforcer()
    
    # Test token limit
    with pytest.raises(LimitExceededException) as exc:
        enforcer.enforce_task_limits(token_cost=TaskLimits.MAX_TOKENS + 1)
    assert "Max tokens" in str(exc.value)
    
    enforcer.current_tokens = 0
    
    # Test recursion limit
    enforcer.current_recursion = TaskLimits.MAX_RECURSION
    with pytest.raises(LimitExceededException) as exc:
        enforcer.enforce_task_limits()
    assert "Max recursion" in str(exc.value)

def test_champion_vs_challenger():
    sandbox = SandboxLab()
    gate = PromotionGate(sandbox)
    
    champion = Scorecard(
        accuracy=0.85, latency=0.5, token_consumption=0.5, api_cost=0.1, 
        memory=0.9, failure_rate=0.05, safety_pass=True, regression_pass=True
    )
    
    # Challenger configured with chunk_size 900 -> sandbox will give it higher accuracy (0.94)
    challenger = CandidateConfiguration(
        experiment_id="exp1",
        config_data={"retrieval": {"chunk_size": 900}}
    )
    
    # Evaluate promotion
    approved = gate.evaluate_champion_vs_challenger(challenger, champion)
    assert approved is True
    
    # Challenger configured with chunk_size 600 -> lower utility
    challenger_bad = CandidateConfiguration(
        experiment_id="exp2",
        config_data={"retrieval": {"chunk_size": 600}}
    )
    
    approved_bad = gate.evaluate_champion_vs_challenger(challenger_bad, champion)
    assert approved_bad is False

def test_mathematical_canary_rollback():
    manager = VersionManager()
    
    v1 = SystemManifest(retrieval="1.0.0")
    manager.deploy_manifest(v1)
    
    v2 = SystemManifest(retrieval="2.0.0")
    manager.deploy_manifest(v2)
    
    assert manager.get_manifest().retrieval == "2.0.0"
    
    # Simulate canary failures
    # Trigger condition: 100 observations, >= 8.7% failure rate
    for _ in range(90):
        manager.record_canary_observation(failed=False)
        
    for _ in range(10):
        manager.record_canary_observation(failed=True) # 10/100 = 10%
        
    # After the 100th observation, rollback should have triggered
    assert manager.get_manifest().retrieval == "1.0.0"

def test_experiment_manager_db_isolation():
    manager = ExperimentManager(db_path="logs/test_evo.db", reasoner=MockReasoner())
    
    pattern = FailurePattern(
        pattern_id="P-184", failure_type="retrieval", observed_insight="mock",
        sample_size=1842, confidence=0.94, possible_causes=["chunk_size"]
    )
    
    candidates = manager.generate_experiment(pattern, {"retrieval": "1.0.0"})
    
    assert len(candidates) > 0
    assert candidates[0].config_data["retrieval"]["chunk_size"] in [1200, 900, 600]
    
    # Check that it actually wrote to evolution db by updating status
    manager.update_candidate_status(candidates[0].candidate_id, "TESTED")
    
    # Assuming no errors thrown, DB operations succeeded.
