import pytest
import time
from agents.executive_agent import ExecutiveAgent
from agents.research_agent import ResearchAgent

def test_executive_agent_retry(mocker):
    agent = ExecutiveAgent()
    
    # Mock the LLM instead of the chain
    mock_invoke = mocker.patch.object(agent.llm, "invoke")
    mock_invoke.side_effect = [
        Exception("[Errno 11001] getaddrinfo failed"),
        mocker.Mock(content="Hello Boss, I recovered!")
    ]
    
    # We need to mock the vault as well to avoid actual DB hits
    mocker.patch.object(agent.vault, "recall_facts", return_value=[])
    mocker.patch.object(agent.vault, "get_mood", return_value={})
    mocker.patch.object(agent.vault, "get_ethical_framework", return_value="standard")
    
    start_time = time.time()
    response = agent.think("Test message")
    duration = time.time() - start_time
    
    # Should have retried (at least 1s delay)
    assert duration >= 1
    assert "recovered" in response
    assert mock_invoke.call_count == 2

def test_research_agent_retry(mocker):
    agent = ResearchAgent()
    
    # Mock the LLM instead of the chain
    mock_invoke = mocker.patch.object(agent.llm, "invoke")
    mock_invoke.side_effect = [
        Exception("429 Resource exhausted"),
        mocker.Mock(content="Cloud is back online.")
    ]
    
    mocker.patch.object(agent.vault, "recall_facts", return_value=[])
    mocker.patch.object(agent.vault, "get_mood", return_value={})
    mocker.patch.object(agent.vault, "get_ethical_framework", return_value="standard")
    
    start_time = time.time()
    response = agent.think("Test research")
    duration = time.time() - start_time
    
    # Should have retried (at least 2s delay)
    assert duration >= 2
    assert "online" in response
    assert mock_invoke.call_count == 2
