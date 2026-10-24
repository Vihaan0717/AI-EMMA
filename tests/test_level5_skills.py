import pytest
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.skill_models import Skill, SkillStatus, CapabilityAction, ExpertiseProfile
from core.skill_registry import SkillRegistry
from backend.simulation_lab import SimulationLab
from core.pattern_detector import PatternDetector
from core.experience_store import ExperienceStore, ExperienceRecord
from core.memory_models import MemoryItem, MemoryType, MemoryAccess, MemoryStatus, MemoryStability, MemoryProvenance
from core.memory_decay import MemoryDecayEngine
from memory.semantic_retrieval import SemanticRetriever

@pytest.fixture(autouse=True)
def clean_level5_dbs():
    db_paths = ["logs/test_skills.db", "logs/test_exp.db", "logs/test_sem.db"]
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)
    yield
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)

def test_pattern_extraction_and_simulation():
    registry = SkillRegistry(db_path="logs/test_skills.db")
    exp_store = ExperienceStore(db_path="logs/test_exp.db")
    detector = PatternDetector(exp_store, registry)
    lab = SimulationLab(registry)
    
    # 1. Pattern Extraction
    candidate = detector.detect_patterns("Atlas", "research")
    assert candidate.status == SkillStatus.CANDIDATE
    
    # 2. Simulation Gate
    passed = lab.evaluate_candidate(candidate)
    assert passed is True
    
    # Verify promotion to ESTABLISHED
    active = registry.get_active_skill("research_skill", "Atlas")
    assert active is not None
    assert active.status == SkillStatus.ESTABLISHED

def test_unauthorized_skill_action():
    registry = SkillRegistry(db_path="logs/test_skills.db")
    lab = SimulationLab(registry)
    
    bad_procedure = [
        CapabilityAction(action="execute_arbitrary_python", arguments={"code": "import os; os.system('rm -rf /')"})
    ]
    
    bad_skill = Skill(
        skill_name="hacker_skill", agent="Hank", domain="security", procedure=bad_procedure
    )
    
    # Static validation should fail
    passed = lab.evaluate_candidate(bad_skill)
    assert passed is False
    assert bad_skill.status == SkillStatus.REJECTED

def test_skill_regression_and_rollback():
    registry = SkillRegistry(db_path="logs/test_skills.db")
    lab = SimulationLab(registry)
    
    # Base v1
    v1 = Skill(
        skill_name="fact_check", agent="Council", domain="truth", version=1, 
        procedure=[CapabilityAction(action="verify_sources")]
    )
    v1.benchmark_score = 0.90
    lab.evaluate_candidate(v1) # Should promote to ESTABLISHED
    
    # New v2 candidate that performs worse
    v2 = Skill(
        skill_name="fact_check", agent="Council", domain="truth", version=2,
        procedure=[CapabilityAction(action="verify_sources")]
    )
    
    # Mocking the benchmark score to be worse than v1
    # We override the deterministic_benchmark method for this test
    def mock_benchmark(skill):
        skill.benchmark_score = 0.85
        return True, "Mock benchmark."
    
    lab._deterministic_benchmark = mock_benchmark
    passed = lab.evaluate_candidate(v2)
    assert passed is False # Fails regression
    
    # Rollback test (Simulate v3 passed but failed in production)
    v3 = Skill(
        skill_name="fact_check", agent="Council", domain="truth", version=3,
        procedure=[CapabilityAction(action="verify_sources")]
    )
    def mock_benchmark_pass(skill):
        skill.benchmark_score = 0.95
        return True, "Mock pass"
    lab._deterministic_benchmark = mock_benchmark_pass
    lab.evaluate_candidate(v3) # Promoted
    
    active = registry.get_active_skill("fact_check", "Council")
    assert active.version == 3
    
    # Oh no, v3 broke! Rollback.
    registry.rollback_skill("fact_check", "Council")
    active_after = registry.get_active_skill("fact_check", "Council")
    assert active_after.version == 1

def test_agent_expertise_tracker():
    profile = ExpertiseProfile(agent_id="Atlas", domain_scores={"research": 0.85})
    # Atlas succeeds verified
    profile.update_metrics(domain="research", success=True, verified=True)
    assert profile.tasks_evaluated == 1
    assert profile.verified_outcomes == 1
    assert profile.domain_scores["research"] == pytest.approx(0.86)

    # Atlas fails
    profile.update_metrics(domain="research", success=False)
    assert profile.failures == 1
    assert profile.domain_scores["research"] == pytest.approx(0.81)

def test_memory_decay():
    retriever = SemanticRetriever(db_path="logs/test_sem.db")
    decay_engine = MemoryDecayEngine(retriever)
    
    prov = MemoryProvenance(experience_id="e1", session_id="s1")
    # We create a temporal memory that is very old
    mem = MemoryItem(
        memory_type=MemoryType.SEMANTIC, access_level=MemoryAccess.GLOBAL_VERIFIED,
        agent_id="Atlas", content="Weather is sunny", status=MemoryStatus.VERIFIED,
        stability=MemoryStability.TEMPORAL, provenance=prov
    )
    # Mock age
    mem.last_verified = "2000-01-01T00:00:00+00:00"
    retriever.add_memory(mem)
    
    decay_engine.process_decay()
    
    store = retriever.memory_store
    decayed = next((m for m in store if m.memory_id == mem.memory_id), None)
    assert decayed.status == MemoryStatus.STALE
