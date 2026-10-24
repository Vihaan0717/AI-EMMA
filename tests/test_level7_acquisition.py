import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.objective_manager import ObjectiveManager
from core.knowledge_graph import KnowledgeGraph, Entity, Relationship
from backend.services.research_agent import ResearchAgent
from backend.services.trainer_agent import TrainerAgent, ProgressivePermissioning
from evolution_lab.sandbox import SandboxLab
from evolution_lab.promotion_gate import PromotionGate
from core.skill_models import SkillStatus

@pytest.fixture(autouse=True)
def clean_level7_dbs():
    db_paths = ["logs/test_knowledge_graph.db"]
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)
    yield
    for p in db_paths:
        if os.path.exists(p):
            os.remove(p)

def test_knowledge_gap_detection():
    manager = ObjectiveManager()
    
    # query with gap
    needs_research, coverage = manager.evaluate_knowledge_gap("Explain X using Y", "known_context")
    assert needs_research is True
    assert "X" in coverage.concepts
    
def test_knowledge_graph_integrity():
    kg = KnowledgeGraph(db_path="logs/test_knowledge_graph.db")
    
    e1 = Entity(name="Python", type="TECHNOLOGY")
    e2 = Entity(name="Java", type="TECHNOLOGY")
    kg.add_entity(e1)
    kg.add_entity(e2)
    
    rel = Relationship(
        source_entity_id=e1.entity_id,
        target_entity_id=e2.entity_id,
        relation_type="competes_with"
    )
    kg.add_relationship(rel)
    
    related = kg.get_related_entities("Python")
    assert len(related) == 1
    assert related[0]["target"] == "Java"
    assert related[0]["relation"] == "competes_with"
    
def test_research_pipeline_validation():
    kg = KnowledgeGraph(db_path="logs/test_knowledge_graph.db")
    researcher = ResearchAgent(knowledge_graph=kg)
    
    memory = researcher.execute_research("Swarm Architecture")
    
    assert memory.verified is True
    assert memory.independent_sources >= 1
    assert memory.confidence > 0.8
    assert "Swarm Architecture" in memory.content
    
    # Verify entity extracted to graph
    related = kg.get_related_entities("Advanced Orchestration")
    assert len(related) == 1
    assert related[0]["target"] == "Swarm Architecture"

def test_trainer_progressive_sandbox():
    sandbox = SandboxLab()
    gate = PromotionGate(sandbox)
    trainer = TrainerAgent(sandbox, gate)
    
    workflow = ["extract_pdf", "clean_text", "save_db"]
    skill = trainer.acquire_skill(workflow, "PDF_Processor")
    
    assert skill.skill_name == "PDF_Processor"
    assert skill.status == SkillStatus.ESTABLISHED
    assert len(skill.procedure) == 3
    assert skill.procedure[0].action == "extract_pdf"
