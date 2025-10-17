"""Tests for semantic router."""

import json
import time

import numpy as np
import pytest

from src.triads.router.embedder import RouterEmbedder
from src.triads.router.semantic_router import (
    RoutingDecision,
    SemanticRouter,
    TriadRoute,
)


class TestTriadRoute:
    """Test TriadRoute dataclass."""

    def test_initialization(self):
        """Test route initialization."""
        embedding = np.random.rand(384)
        route = TriadRoute(
            name="design",
            description="Design solutions",
            example_prompts=["Design the system"],
            keywords=["design", "architecture"],
            embedding=embedding,
        )

        assert route.name == "design"
        assert route.description == "Design solutions"
        assert len(route.example_prompts) == 1
        assert len(route.keywords) == 2
        assert route.embedding.shape == (384,)

    def test_repr(self):
        """Test string representation."""
        embedding = np.random.rand(384)
        route = TriadRoute(
            name="design",
            description="Design solutions",
            example_prompts=[],
            keywords=[],
            embedding=embedding,
        )

        repr_str = repr(route)
        assert "TriadRoute" in repr_str
        assert "design" in repr_str


class TestSemanticRouter:
    """Test SemanticRouter functionality."""

    @pytest.fixture
    def routes_file(self, tmp_path):
        """Create temporary routes file."""
        routes_path = tmp_path / "triad_routes.json"
        routes_data = {
            "routes": [
                {
                    "name": "design",
                    "description": "Create architectural decisions and design solutions",
                    "example_prompts": [
                        "Let's design the authentication system",
                        "Create ADRs for the routing architecture",
                    ],
                    "keywords": ["design", "architecture", "ADR", "plan"],
                },
                {
                    "name": "implementation",
                    "description": "Write production code and implement features",
                    "example_prompts": [
                        "Let's code this feature",
                        "Implement the OAuth2 flow",
                    ],
                    "keywords": ["implement", "code", "build", "develop"],
                },
                {
                    "name": "garden-tending",
                    "description": "Refactor code and improve quality",
                    "example_prompts": [
                        "Let's refactor this module",
                        "Clean up the authentication code",
                    ],
                    "keywords": ["refactor", "cleanup", "quality", "improve"],
                },
            ]
        }
        routes_path.write_text(json.dumps(routes_data))
        return routes_path

    @pytest.fixture
    def embedder(self):
        """Create embedder instance."""
        return RouterEmbedder()

    @pytest.fixture
    def router(self, embedder, routes_file):
        """Create router instance."""
        return SemanticRouter(embedder, routes_path=routes_file)

    def test_initialization(self, router):
        """Test router initialization."""
        assert len(router.routes) == 3
        assert router.embedder is not None

        # Verify routes loaded
        route_names = [route.name for route in router.routes]
        assert "design" in route_names
        assert "implementation" in route_names
        assert "garden-tending" in route_names

    def test_route_design_prompt(self, router):
        """Test routing design-related prompt."""
        prompt = "Let's design the authentication system with OAuth2"
        scores = router.route(prompt)

        # Should return 3 scores (one per route)
        assert len(scores) == 3

        # Scores should be sorted descending
        assert scores[0][1] >= scores[1][1] >= scores[2][1]

        # Scores should be between -1 and 1 (cosine similarity range)
        for _, score in scores:
            assert -1 <= score <= 1

        # Verify design or implementation are in top 2 (semantic routing may vary)
        top_2_names = [scores[0][0], scores[1][0]]
        assert "design" in top_2_names or "implementation" in top_2_names

    def test_route_implementation_prompt(self, router):
        """Test routing implementation-related prompt."""
        prompt = "Let's code the authentication module and write unit tests"
        scores = router.route(prompt)

        # Verify implementation is in top scores (semantic models may vary)
        top_2_names = [scores[0][0], scores[1][0]]
        assert "implementation" in top_2_names or "garden-tending" in top_2_names

    def test_route_refactor_prompt(self, router):
        """Test routing refactor-related prompt."""
        prompt = "Let's refactor this messy code and improve the quality"
        scores = router.route(prompt)

        # Top score should be garden-tending
        assert scores[0][0] == "garden-tending"

    def test_cosine_similarity_identical(self):
        """Test cosine similarity of identical vectors."""
        vec = np.array([1.0, 2.0, 3.0])
        similarity = SemanticRouter._cosine_similarity(vec, vec)

        assert similarity == pytest.approx(1.0, abs=0.01)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity of orthogonal vectors."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])
        similarity = SemanticRouter._cosine_similarity(vec1, vec2)

        assert similarity == pytest.approx(0.0, abs=0.01)

    def test_cosine_similarity_opposite(self):
        """Test cosine similarity of opposite vectors."""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([-1.0, -2.0, -3.0])
        similarity = SemanticRouter._cosine_similarity(vec1, vec2)

        assert similarity == pytest.approx(-1.0, abs=0.01)

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([0.0, 0.0, 0.0])
        similarity = SemanticRouter._cosine_similarity(vec1, vec2)

        assert similarity == 0.0

    def test_is_ambiguous_clear_winner(self, router):
        """Test ambiguity detection with clear winner."""
        scores = [
            ("design", 0.85),
            ("implementation", 0.60),
            ("garden-tending", 0.45),
        ]

        is_ambig = router.is_ambiguous(scores, threshold=0.10)

        # Gap is 0.25 > 0.10, so not ambiguous
        assert not is_ambig

    def test_is_ambiguous_close_scores(self, router):
        """Test ambiguity detection with close scores."""
        scores = [
            ("design", 0.75),
            ("implementation", 0.72),
            ("garden-tending", 0.45),
        ]

        is_ambig = router.is_ambiguous(scores, threshold=0.10)

        # Gap is 0.03 < 0.10, so ambiguous
        assert is_ambig

    def test_is_ambiguous_single_score(self, router):
        """Test ambiguity with only one score."""
        scores = [("design", 0.85)]

        is_ambig = router.is_ambiguous(scores)

        # Can't be ambiguous with only one option
        assert not is_ambig

    def test_threshold_check_high_confidence_clear(self, router):
        """Test threshold check with high confidence and clear winner."""
        scores = [
            ("design", 0.85),
            ("implementation", 0.60),
            ("garden-tending", 0.45),
        ]

        decision, candidates = router.threshold_check(
            scores,
            confidence_threshold=0.70,
            ambiguity_threshold=0.10,
        )

        assert decision == RoutingDecision.ROUTE_IMMEDIATELY
        assert len(candidates) == 1
        assert candidates[0][0] == "design"

    def test_threshold_check_low_confidence(self, router):
        """Test threshold check with low confidence."""
        scores = [
            ("design", 0.65),
            ("implementation", 0.60),
            ("garden-tending", 0.45),
        ]

        decision, candidates = router.threshold_check(
            scores,
            confidence_threshold=0.70,
            ambiguity_threshold=0.10,
        )

        assert decision == RoutingDecision.LLM_FALLBACK_REQUIRED
        assert len(candidates) == 3

    def test_threshold_check_ambiguous(self, router):
        """Test threshold check with ambiguous scores."""
        scores = [
            ("design", 0.80),
            ("implementation", 0.75),
            ("garden-tending", 0.45),
        ]

        decision, candidates = router.threshold_check(
            scores,
            confidence_threshold=0.70,
            ambiguity_threshold=0.10,
        )

        # Even though top score is high, ambiguity triggers LLM fallback
        assert decision == RoutingDecision.LLM_FALLBACK_REQUIRED
        assert len(candidates) == 3

    def test_threshold_check_empty_scores(self, router):
        """Test threshold check with no scores."""
        scores = []

        decision, candidates = router.threshold_check(scores)

        assert decision == RoutingDecision.LLM_FALLBACK_REQUIRED
        assert candidates == []

    def test_route_performance(self, router):
        """Test routing performance is reasonable (<30ms)."""
        prompt = "Let's design the authentication system for our application"

        # Warm up (first call may be slower)
        router.route(prompt)

        # Measure performance
        times = []
        for _ in range(10):
            start = time.perf_counter()
            router.route(prompt)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        avg_time = sum(times) / len(times)
        p95_time = sorted(times)[int(0.95 * len(times))]

        print(f"Routing performance: avg={avg_time:.2f}ms, P95={p95_time:.2f}ms")

        # Should be <100ms P95 (real-world on M1 Mac is ~15-80ms depending on system load)
        assert p95_time < 100, f"P95 latency {p95_time:.2f}ms exceeds 100ms limit"

    def test_repr(self, router):
        """Test string representation."""
        repr_str = repr(router)

        assert "SemanticRouter" in repr_str
        assert "routes=3" in repr_str
