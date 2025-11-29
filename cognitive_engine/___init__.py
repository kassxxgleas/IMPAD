"""
Cognitive Engine - LLM-powered skill analysis for GlassBox
Analyzes candidate explanations and rates clarity metrics.
"""

from .clarity_analyzer import ClarityAnalyzer
from .fake_llm import FakeLLM

__version__ = "0.1.0"
__all__ = ["ClarityAnalyzer", "FakeLLM"]
