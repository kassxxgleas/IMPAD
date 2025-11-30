"""
FakeLLM - Mock LLM for testing without API key.
Useful for development, testing, and when API is down.
"""

import random
from typing import Dict, Any


class FakeLLM:
    """
    Mock LLM that returns random or fixed scores.
    Useful for testing without OpenAI API key.
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize FakeLLM.
        
        Args:
            seed: Optional seed for reproducible results
        """
        if seed is not None:
            random.seed(seed)
    
    def analyze(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze transcript and return mock scores.
        
        Args:
            transcript: Text to analyze
        
        Returns:
            dict: {coherence, terminology, completeness, comment}
        """
        if not transcript or len(transcript.strip()) < 10:
            return {
                "coherence": 0,
                "terminology": 0,
                "completeness": 0,
                "comment": "Error: Transcript too short"
            }
        
        # Generate random scores in ranges
        coherence = random.randint(50, 95)
        terminology = random.randint(50, 90)
        completeness = random.randint(45, 85)
        
        # Different comments
        comments = [
            "Good logical flow, could add more edge cases.",
            "Clear explanation, terminology needs improvement.",
            "Comprehensive analysis, minor gaps in structure.",
            "Strong technical vocabulary, consider more alternatives.",
            "Well-organized, address constraints more explicitly."
        ]
        
        comment = random.choice(comments)
        
        return {
            "coherence": coherence,
            "terminology": terminology,
            "completeness": completeness,
            "comment": comment
        }

    def analyze_code(self, code: str) -> int:
        """
        Analyze code quality and return a score (0-100).
        """
        if not code or len(code.strip()) < 10:
            return 0
            
        # Random score for mock mode
        return random.randint(60, 95)
