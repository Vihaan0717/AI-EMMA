"""
JARVIS Smart Reasoning System
Zero AI-API dependency. Learns. Adapts. Gets smarter every use.
"""

from .smart_engine import SmartReasoningEngine
from .pattern_learner import PatternLearner
from .knowledge_base import KnowledgeBase
from .web_fallback import WebFallback
from .analyzer import DeepAnalyzer

__all__ = [
    "SmartReasoningEngine",
    "PatternLearner", 
    "KnowledgeBase",
    "WebFallback",
    "DeepAnalyzer"
]

VERSION = "1.0.0"
