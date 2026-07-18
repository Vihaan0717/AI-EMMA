import asyncio
import pytest
from agents.response_agent import SentientMirrorPipeline

@pytest.mark.asyncio
async def test_mirror_analysis():
    pipeline = SentientMirrorPipeline()
    user_input = "Namaste Jarvis, where are my keys? Hau, find them."
    analysis = await pipeline.analyze_input(user_input)
    print(f"\nDEBUG ANALYSIS: {analysis}")
    
    assert "intent" in analysis
    assert "slang_dict" in analysis
    # Should detect religious/regional slang
    slang = [s.lower() for s in analysis["slang_dict"]]
    assert any(x in slang for x in ["namaste", "hau"])

@pytest.mark.asyncio
async def test_full_mirror_process():
    pipeline = SentientMirrorPipeline()
    user_input = "Namaste Jarvis, tell me a joke."
    response = await pipeline.process(user_input)
    
    # Should be mirrored (no "As an AI")
    assert "As an AI" not in response
    # Should probably contain some character
    assert len(response) > 0
    # Search for cultural closings if deconstruction worked
    # (Checking for specific words might be flaky with LLMs, but we can check tone)
    print(f"Mirrored Reply: {response}")
