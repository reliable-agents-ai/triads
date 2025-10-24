#!/usr/bin/env python3
"""
Test Phase 2 fixes:
1. Q&A pattern coverage expansion
2. Syntax error fix in agent_templates.py
"""

import sys
from pathlib import Path

# Add hooks to path
repo_root = Path(__file__).parent
if str(repo_root / "hooks") not in sys.path:
    sys.path.insert(0, str(repo_root / "hooks"))

from user_prompt_submit import detect_work_request


def test_qa_patterns_fix():
    """Test that 'can you', 'could you', 'would you' patterns are recognized as Q&A"""

    # Test cases that should return empty dict (Q&A, not work)
    qa_test_cases = [
        "Can you implement OAuth2?",
        "can you add this feature?",
        "Could you build a dashboard?",
        "could you create a new component?",
        "Would you fix this bug?",
        "would you help me understand?",
        # Edge cases
        "Can you explain how to implement OAuth2?",  # Mixed - 'explain' should trigger first
        "Could you tell me about the implementation?",  # Mixed - 'tell me about' should trigger first
    ]

    print("Testing Q&A pattern detection...")
    print("=" * 60)

    for i, test_case in enumerate(qa_test_cases, 1):
        result = detect_work_request(test_case)
        if result == {}:
            print(f"✓ Test {i}: PASS - '{test_case}' → Q&A (empty dict)")
        else:
            print(f"✗ Test {i}: FAIL - '{test_case}' → {result}")
            print(f"  Expected: empty dict (Q&A)")
            print(f"  Got: {result} (work request)")
            return False

    print("=" * 60)
    print("✓ All Q&A pattern tests PASSED")
    return True


def test_work_patterns_still_work():
    """Verify that legitimate work requests are still detected"""

    work_test_cases = [
        ("Implement OAuth2", "feature"),
        ("Add user authentication", "feature"),
        ("Fix the router crash", "bug"),
        ("Refactor the messy code", "refactor"),
    ]

    print("\nTesting work pattern detection (should still work)...")
    print("=" * 60)

    for i, (test_case, expected_type) in enumerate(work_test_cases, 1):
        result = detect_work_request(test_case)
        if result and result.get('type') == expected_type:
            print(f"✓ Test {i}: PASS - '{test_case}' → {expected_type}")
        else:
            print(f"✗ Test {i}: FAIL - '{test_case}'")
            print(f"  Expected: type={expected_type}")
            print(f"  Got: {result}")
            return False

    print("=" * 60)
    print("✓ All work pattern tests PASSED")
    return True


def test_syntax_error_fixed():
    """Verify agent_templates.py compiles without errors"""

    print("\nTesting syntax error fix...")
    print("=" * 60)

    try:
        import py_compile
        template_path = repo_root / "src" / "triads" / "templates" / "agent_templates.py"
        py_compile.compile(str(template_path), doraise=True)
        print("✓ agent_templates.py compiles successfully")
        print("=" * 60)
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error still present: {e}")
        print("=" * 60)
        return False


def main():
    """Run all Phase 2 fix tests"""

    print("\n" + "=" * 60)
    print("PHASE 2 FIX VALIDATION")
    print("=" * 60)

    results = []

    # Test 1: Q&A patterns
    results.append(("Q&A Pattern Expansion", test_qa_patterns_fix()))

    # Test 2: Work patterns still work
    results.append(("Work Pattern Detection", test_work_patterns_still_work()))

    # Test 3: Syntax error fixed
    results.append(("Syntax Error Fix", test_syntax_error_fixed()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")

    all_passed = all(result for _, result in results)

    print("=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
