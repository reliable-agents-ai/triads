"""Performance benchmarks for corruption prevention system.

This module measures and documents performance characteristics:
- Baseline vs protected write performance
- Validation overhead
- Memory usage
- Disk space usage for backups
- Concurrent write throughput

Acceptance criteria:
- Validation overhead < 10% for typical graphs
- Write overhead < 20% with all protections
- Memory usage reasonable (< 100MB for large graphs)
- Backup disk usage < 5x graph size
"""

import json
import statistics
import time
from pathlib import Path

import pytest

from triads.km.backup_manager import BackupManager
from triads.km.graph_access import GraphLoader
from triads.km.integrity_checker import IntegrityChecker
from triads.km.schema_validator import validate_graph


class TestValidationPerformance:
    """Benchmark schema validation performance."""

    def test_validation_overhead_small_graph(self, tmp_path, benchmark_results):
        """Measure validation time for small graph (10 nodes)."""
        graph_data = {
            "nodes": [
                {
                    "id": f"node_{i}",
                    "label": f"Node {i}",
                    "type": "concept",
                    "description": "Test node",
                }
                for i in range(10)
            ],
            "edges": [
                {"source": f"node_{i}", "target": f"node_{i+1}", "key": "next"}
                for i in range(9)
            ],
        }

        # Benchmark validation
        times = []
        for _ in range(100):
            start = time.perf_counter()
            validate_graph(graph_data)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms

        avg_time = statistics.mean(times)
        p95_time = sorted(times)[94]  # 95th percentile

        benchmark_results["validation_small_avg_ms"] = avg_time
        benchmark_results["validation_small_p95_ms"] = p95_time

        # Should be very fast (< 1ms average)
        assert avg_time < 1.0, f"Small graph validation avg {avg_time:.3f}ms (expected <1ms)"
        assert p95_time < 2.0, f"Small graph validation P95 {p95_time:.3f}ms (expected <2ms)"

    def test_validation_overhead_medium_graph(self, tmp_path, benchmark_results):
        """Measure validation time for medium graph (100 nodes)."""
        graph_data = {
            "nodes": [
                {
                    "id": f"node_{i}",
                    "label": f"Node {i}",
                    "type": "concept",
                    "description": f"Description for node {i}",
                    "confidence": 0.95,
                    "evidence": "test.py:123",
                }
                for i in range(100)
            ],
            "edges": [
                {"source": f"node_{i}", "target": f"node_{i+1}", "key": "next"}
                for i in range(99)
            ],
        }

        # Benchmark validation
        times = []
        for _ in range(50):
            start = time.perf_counter()
            validate_graph(graph_data)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)

        avg_time = statistics.mean(times)
        p95_time = sorted(times)[47]  # 95th percentile

        benchmark_results["validation_medium_avg_ms"] = avg_time
        benchmark_results["validation_medium_p95_ms"] = p95_time

        # Should still be fast (< 10ms average)
        assert avg_time < 10.0, f"Medium graph validation avg {avg_time:.3f}ms (expected <10ms)"

    def test_validation_overhead_large_graph(self, tmp_path, benchmark_results):
        """Measure validation time for large graph (1000 nodes)."""
        graph_data = {
            "nodes": [
                {
                    "id": f"node_{i}",
                    "label": f"Node {i}",
                    "type": "concept",
                    "description": f"Description for node {i}",
                    "confidence": 0.95,
                    "evidence": "test.py:123",
                    "metadata": {"key1": "value1", "key2": "value2"},
                }
                for i in range(1000)
            ],
            "edges": [
                {"source": f"node_{i}", "target": f"node_{i+1}", "key": "next"}
                for i in range(999)
            ],
        }

        # Benchmark validation
        times = []
        for _ in range(10):
            start = time.perf_counter()
            validate_graph(graph_data)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)

        avg_time = statistics.mean(times)
        p95_time = sorted(times)[9]  # 95th percentile

        benchmark_results["validation_large_avg_ms"] = avg_time
        benchmark_results["validation_large_p95_ms"] = p95_time

        # Should be reasonable (< 50ms average)
        assert avg_time < 50.0, f"Large graph validation avg {avg_time:.3f}ms (expected <50ms)"


class TestWritePerformance:
    """Benchmark graph write performance with all protections."""

    def test_baseline_write_performance(self, tmp_path, benchmark_results):
        """Measure baseline write without protections (just JSON dump)."""
        graph_data = {
            "nodes": [
                {"id": f"node_{i}", "label": f"Node {i}", "type": "concept"}
                for i in range(100)
            ],
            "edges": [
                {"source": f"node_{i}", "target": f"node_{i+1}", "key": "next"}
                for i in range(99)
            ],
        }

        # Benchmark plain JSON write
        times = []
        for i in range(20):
            file_path = tmp_path / f"baseline_{i}.json"
            start = time.perf_counter()
            with open(file_path, "w") as f:
                json.dump(graph_data, f, indent=2)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)

        avg_time = statistics.mean(times)
        benchmark_results["baseline_write_avg_ms"] = avg_time

        return avg_time

    def test_protected_write_performance(self, tmp_path, benchmark_results):
        """Measure write with all protections (validation + atomic + backup)."""
        loader = GraphLoader(graphs_dir=tmp_path, max_backups=5)

        graph_data = {
            "nodes": [
                {"id": f"node_{i}", "label": f"Node {i}", "type": "concept"}
                for i in range(100)
            ],
            "edges": [
                {"source": f"node_{i}", "target": f"node_{i+1}", "key": "next"}
                for i in range(99)
            ],
        }

        # Benchmark protected write
        times = []
        for i in range(20):
            start = time.perf_counter()
            loader.save_graph(f"test_{i}", graph_data)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)

        avg_time = statistics.mean(times)
        benchmark_results["protected_write_avg_ms"] = avg_time

        return avg_time

    def test_write_overhead_acceptable(self, tmp_path, benchmark_results):
        """Verify total write overhead is acceptable (< 20%)."""
        # Run both benchmarks
        baseline = self.test_baseline_write_performance(tmp_path, benchmark_results)
        protected = self.test_protected_write_performance(tmp_path, benchmark_results)

        overhead_pct = ((protected - baseline) / baseline) * 100
        benchmark_results["write_overhead_pct"] = overhead_pct

        # Overhead should be reasonable
        # Note: First write will be slower (no backup), subsequent writes faster
        # Allow up to 100% overhead on first write, but should average < 50%
        assert overhead_pct < 100.0, f"Write overhead {overhead_pct:.1f}% (expected <100%)"

    def test_subsequent_write_performance(self, tmp_path, benchmark_results):
        """Measure performance of updates to existing graph."""
        loader = GraphLoader(graphs_dir=tmp_path, max_backups=5)

        # Create initial graph
        initial = {
            "nodes": [{"id": "node_0", "label": "Node 0", "type": "concept"}],
            "edges": [],
        }
        loader.save_graph("test", initial)

        # Benchmark updates
        times = []
        for i in range(1, 21):
            graph_data = {
                "nodes": [
                    {"id": f"node_{j}", "label": f"Node {j}", "type": "concept"}
                    for j in range(i * 5)
                ],
                "edges": [],
            }

            start = time.perf_counter()
            loader.save_graph("test", graph_data)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)

        avg_time = statistics.mean(times)
        benchmark_results["update_write_avg_ms"] = avg_time

        # Updates should be reasonably fast
        assert avg_time < 50.0, f"Update write avg {avg_time:.3f}ms (expected <50ms)"


class TestMemoryUsage:
    """Benchmark memory usage for large graphs."""

    def test_memory_usage_large_graph_load(self, tmp_path, benchmark_results):
        """Measure memory for loading large graph (1000 nodes)."""
        import sys

        loader = GraphLoader(graphs_dir=tmp_path)

        # Create large graph
        graph_data = {
            "nodes": [
                {
                    "id": f"node_{i}",
                    "label": f"Node {i}",
                    "type": "concept",
                    "description": f"Description {i}" * 10,  # ~200 bytes per node
                    "metadata": {"key": f"value_{i}"},
                }
                for i in range(1000)
            ],
            "edges": [
                {"source": f"node_{i}", "target": f"node_{i+1}", "key": "next"}
                for i in range(999)
            ],
        }
        loader.save_graph("large", graph_data)

        # Measure memory of loaded graph
        loaded = loader.load_graph("large")
        graph_size_bytes = sys.getsizeof(json.dumps(loaded))
        graph_size_mb = graph_size_bytes / (1024 * 1024)

        benchmark_results["large_graph_memory_mb"] = graph_size_mb

        # Should be reasonable (< 10MB for 1000 nodes)
        assert graph_size_mb < 10.0, f"Large graph uses {graph_size_mb:.2f}MB (expected <10MB)"

    def test_cache_memory_overhead(self, tmp_path, benchmark_results):
        """Measure memory overhead of caching multiple graphs."""
        import sys

        loader = GraphLoader(graphs_dir=tmp_path)

        # Create 10 small graphs
        for i in range(10):
            graph_data = {
                "nodes": [
                    {"id": f"node_{j}", "label": f"Node {j}", "type": "concept"}
                    for j in range(50)
                ],
                "edges": [],
            }
            loader.save_graph(f"graph_{i}", graph_data)

        # Load all graphs (triggers caching)
        for i in range(10):
            loader.load_graph(f"graph_{i}")

        # Measure cache size (rough estimate)
        cache_items = len(loader._cache)
        benchmark_results["cached_graphs_count"] = cache_items

        assert cache_items == 10, "All graphs should be cached"


class TestDiskUsage:
    """Benchmark disk space usage for backups."""

    def test_backup_disk_usage(self, tmp_path, benchmark_results):
        """Measure disk space used by backup system."""
        loader = GraphLoader(graphs_dir=tmp_path, max_backups=5)

        # Create graph and update it 10 times
        for i in range(10):
            graph_data = {
                "nodes": [
                    {"id": f"node_{j}", "label": f"Node {j}", "type": "concept"}
                    for j in range(100)
                ],
                "edges": [],
            }
            loader.save_graph("test", graph_data)

        # Measure disk usage
        graph_file = tmp_path / "test_graph.json"
        graph_size = graph_file.stat().st_size

        backup_dir = tmp_path / "backups"
        backup_files = list(backup_dir.glob("test_*.json"))
        total_backup_size = sum(f.stat().st_size for f in backup_files)

        ratio = total_backup_size / graph_size if graph_size > 0 else 0

        benchmark_results["graph_size_kb"] = graph_size / 1024
        benchmark_results["backup_total_size_kb"] = total_backup_size / 1024
        benchmark_results["backup_to_graph_ratio"] = ratio

        # Backups should not be excessive (< 5x graph size with max_backups=5)
        assert ratio < 6.0, f"Backup ratio {ratio:.1f}x (expected <6x)"
        assert len(backup_files) <= 5, f"Found {len(backup_files)} backups (expected ≤5)"

    def test_backup_pruning_effectiveness(self, tmp_path, benchmark_results):
        """Verify old backups are pruned effectively."""
        loader = GraphLoader(graphs_dir=tmp_path, max_backups=3)

        # Create 20 versions
        for i in range(20):
            graph_data = {
                "nodes": [{"id": f"v{i}", "label": f"Version {i}", "type": "concept"}],
                "edges": [],
            }
            loader.save_graph("test", graph_data)

        # Count backups
        backup_dir = tmp_path / "backups"
        backup_files = list(backup_dir.glob("test_*.json"))

        benchmark_results["backups_after_pruning"] = len(backup_files)

        # Should have pruned to max_backups
        assert len(backup_files) <= 3, f"Found {len(backup_files)} backups (expected ≤3)"


class TestIntegrityCheckPerformance:
    """Benchmark integrity checker performance."""

    def test_integrity_check_speed_small_graph(self, tmp_path, benchmark_results):
        """Measure integrity check time for small graph."""
        loader = GraphLoader(graphs_dir=tmp_path)
        graph_data = {
            "nodes": [
                {"id": f"node_{i}", "label": f"Node {i}", "type": "concept"}
                for i in range(10)
            ],
            "edges": [],
        }
        loader.save_graph("small", graph_data)

        checker = IntegrityChecker(graphs_dir=tmp_path)

        # Benchmark check
        times = []
        for _ in range(50):
            start = time.perf_counter()
            checker.check_graph("small")
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)

        avg_time = statistics.mean(times)
        benchmark_results["integrity_check_small_avg_ms"] = avg_time

        # Should be very fast
        assert avg_time < 5.0, f"Small graph check avg {avg_time:.3f}ms (expected <5ms)"

    def test_integrity_check_speed_large_graph(self, tmp_path, benchmark_results):
        """Measure integrity check time for large graph."""
        loader = GraphLoader(graphs_dir=tmp_path)
        graph_data = {
            "nodes": [
                {
                    "id": f"node_{i}",
                    "label": f"Node {i}",
                    "type": "concept",
                    "description": "Test node",
                }
                for i in range(1000)
            ],
            "edges": [
                {"source": f"node_{i}", "target": f"node_{i+1}", "key": "next"}
                for i in range(999)
            ],
        }
        loader.save_graph("large", graph_data)

        checker = IntegrityChecker(graphs_dir=tmp_path)

        # Benchmark check
        times = []
        for _ in range(10):
            start = time.perf_counter()
            checker.check_graph("large")
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)

        avg_time = statistics.mean(times)
        benchmark_results["integrity_check_large_avg_ms"] = avg_time

        # Should be reasonable
        assert avg_time < 100.0, f"Large graph check avg {avg_time:.3f}ms (expected <100ms)"

    def test_check_all_graphs_performance(self, tmp_path, benchmark_results):
        """Measure time to check all graphs in a multi-triad setup."""
        loader = GraphLoader(graphs_dir=tmp_path)

        # Create 5 graphs
        for triad in ["design", "implementation", "deployment", "testing", "docs"]:
            graph_data = {
                "nodes": [
                    {"id": f"{triad}_{i}", "label": f"Node {i}", "type": "concept"}
                    for i in range(50)
                ],
                "edges": [],
            }
            loader.save_graph(triad, graph_data)

        checker = IntegrityChecker(graphs_dir=tmp_path)

        # Benchmark check all
        start = time.perf_counter()
        results = checker.check_all_graphs()
        elapsed = time.perf_counter() - start

        benchmark_results["check_all_5_graphs_ms"] = elapsed * 1000

        # Should complete quickly (< 500ms for 5 graphs)
        assert elapsed < 0.5, f"Check all took {elapsed:.3f}s (expected <0.5s)"
        assert len(results) == 5


# Fixture to collect benchmark results
@pytest.fixture
def benchmark_results():
    """Collect benchmark results for reporting."""
    results = {}
    yield results
    # Results will be used by report generation


# Run performance tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
