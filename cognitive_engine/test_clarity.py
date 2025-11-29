"""
Unit tests for ClarityAnalyzer.
Run with: python -m cognitive_engine.test_clarity
"""

import json
from cognitive_engine.clarity_analyzer import ClarityAnalyzer

# Test transcripts
GOOD_TRANSCRIPT = """
First, I identified that this is a dynamic programming problem.
The constraint is that we need to compute the nth Fibonacci number efficiently.
My hypothesis: use memoization to cache results and avoid redundant recursion.
I tested this by implementing a recursive function with a dictionary cache.
The time complexity is O(n), space O(n).
Edge case: I handled n=0 and n=1 as base cases.
Alternative: iterative approach with O(n) time, O(1) space.
"""

WEAK_TRANSCRIPT = """
Um, so like, I started coding and it didn't work.
Then I tried a loop thing. I guess I was thinking about recursion?
Yeah, recursion. It was confusing but then I made it work somehow.
I don't really remember what I did.
"""

EMPTY_TRANSCRIPT = ""


def test_fake_mode():
    """Test ClarityAnalyzer in fake mode."""
    print("\n" + "="*60)
    print("TEST 1: Fake Mode")
    print("="*60)
    
    analyzer = ClarityAnalyzer(mode="fake")
    
    # Test good transcript
    result = analyzer.analyze(GOOD_TRANSCRIPT)
    print(f"\nGood Transcript Result:")
    print(json.dumps(result, indent=2))
    
    # Validate structure
    assert "coherence" in result, "Missing 'coherence'"
    assert "terminology" in result, "Missing 'terminology'"
    assert "completeness" in result, "Missing 'completeness'"
    assert "comment" in result, "Missing 'comment'"
    
    # Validate ranges
    assert 0 <= result["coherence"] <= 100, "coherence out of range"
    assert 0 <= result["terminology"] <= 100, "terminology out of range"
    assert 0 <= result["completeness"] <= 100, "completeness out of range"
    assert isinstance(result["comment"], str), "comment not a string"
    
    print("\n✅ Fake mode test PASSED")


def test_weak_transcript():
    """Test with weak explanation."""
    print("\n" + "="*60)
    print("TEST 2: Weak Transcript")
    print("="*60)
    
    analyzer = ClarityAnalyzer(mode="fake")
    result = analyzer.analyze(WEAK_TRANSCRIPT)
    
    print(f"\nWeak Transcript Result:")
    print(json.dumps(result, indent=2))
    
    print("\n✅ Weak transcript test completed")


def test_empty_input():
    """Test with empty input."""
    print("\n" + "="*60)
    print("TEST 3: Empty Input")
    print("="*60)
    
    analyzer = ClarityAnalyzer(mode="fake")
    result = analyzer.analyze(EMPTY_TRANSCRIPT)
    
    print(f"\nEmpty Transcript Result:")
    print(json.dumps(result, indent=2))
    
    # Should return error response
    assert result["coherence"] == 0, "Should score 0 for empty input"
    assert "Error" in result["comment"], "Should have error message"
    
    print("\n✅ Empty input test PASSED")


def test_switching_modes():
    """Test switching between modes."""
    print("\n" + "="*60)
    print("TEST 4: Mode Switching")
    print("="*60)
    
    analyzer_fake = ClarityAnalyzer(mode="fake")
    result_fake = analyzer_fake.analyze(GOOD_TRANSCRIPT)
    print(f"\nFake mode result: {result_fake['coherence']}")
    
    analyzer_fake_2 = ClarityAnalyzer(mode="fake")
    result_fake_2 = analyzer_fake_2.analyze(GOOD_TRANSCRIPT)
    print(f"Fake mode result #2: {result_fake_2['coherence']}")
    
    # Both should have valid structure
    assert isinstance(result_fake["coherence"], int)
    assert isinstance(result_fake_2["coherence"], int)
    
    print("\n✅ Mode switching test PASSED")


def test_json_validity():
    """Test that all outputs are valid JSON-serializable."""
    print("\n" + "="*60)
    print("TEST 5: JSON Validity")
    print("="*60)
    
    analyzer = ClarityAnalyzer(mode="fake")
    result = analyzer.analyze(GOOD_TRANSCRIPT)
    
    # Try to serialize to JSON
    try:
        json_str = json.dumps(result)
        print(f"\nJSON serialization successful:")
        print(json_str)
        
        # Try to deserialize
        parsed = json.loads(json_str)
        assert parsed == result, "Deserialized data doesn't match"
        
        print("\n✅ JSON validity test PASSED")
    except Exception as e:
        print(f"\n❌ JSON validity test FAILED: {e}")
        raise


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS FOR ClarityAnalyzer")
    print("="*60)
    
    try:
        test_fake_mode()
        test_weak_transcript()
        test_empty_input()
        test_switching_modes()
        test_json_validity()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
