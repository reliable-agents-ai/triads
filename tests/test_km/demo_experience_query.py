#!/usr/bin/env python3
"""Demo script showing ExperienceQueryEngine in action.

This demonstrates Day 1 deliverable: Experience Query Engine with
high-performance relevance scoring.
"""

import time
from pathlib import Path

from triads.km.experience_query import ExperienceQueryEngine


def main():
    """Run demo of experience query engine."""
    print("=" * 70)
    print("EXPERIENCE QUERY ENGINE - DAY 1 DEMO")
    print("=" * 70)
    print()

    # Create engine with test fixture
    fixture_dir = Path(__file__).parent / "fixtures"
    engine = ExperienceQueryEngine(graphs_dir=fixture_dir)

    # Demo 1: Get all CRITICAL knowledge (for SessionStart)
    print("1. CRITICAL Knowledge (shown at session start)")
    print("-" * 70)
    critical = engine.get_critical_knowledge()
    print(f"Found {len(critical)} CRITICAL item(s):\n")

    for item in critical:
        print(item.formatted_text)
        print()

    # Demo 2: Query for specific tool context
    print("\n2. Query for Tool Context: Write to plugin.json")
    print("-" * 70)

    start = time.perf_counter()
    results = engine.query_for_tool_use(
        tool_name="Write",
        tool_input={"file_path": "/path/to/plugin.json"},
        cwd=".",
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"Query completed in {elapsed_ms:.2f}ms")
    print(f"Found {len(results)} relevant item(s):\n")

    for i, item in enumerate(results[:3], 1):  # Show top 3
        print(f"Result {i}: [{item.priority}] {item.label}")
        print(f"Relevance: {item.relevance_score:.2f}")
        print(f"Process Type: {item.process_type}")
        print()

    # Demo 3: Show formatted output for injection
    print("\n3. Formatted Output (ready for injection into context)")
    print("-" * 70)
    if results:
        print("Top result formatted for display:\n")
        print(results[0].formatted_text)
        print()

    # Demo 4: Performance test
    print("\n4. Performance Test (10 queries)")
    print("-" * 70)

    times = []
    for i in range(10):
        start = time.perf_counter()
        engine.query_for_tool_use(
            tool_name="Write",
            tool_input={"file_path": f"/path/to/file{i}.py"},
            cwd=".",
        )
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

    times.sort()
    p50 = times[len(times) // 2]
    p95 = times[int(len(times) * 0.95)]

    print(f"P50: {p50:.2f}ms")
    print(f"P95: {p95:.2f}ms")
    print(f"Min: {min(times):.2f}ms")
    print(f"Max: {max(times):.2f}ms")
    print()

    if p95 < 100:
        print("✅ Performance target met: P95 < 100ms")
    else:
        print(f"⚠️ Performance target missed: P95 {p95:.2f}ms > 100ms")

    print()
    print("=" * 70)
    print("Day 1 Complete: Experience Query Engine operational!")
    print("=" * 70)


if __name__ == "__main__":
    main()
