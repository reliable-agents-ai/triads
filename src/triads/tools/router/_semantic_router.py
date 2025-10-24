"""
Semantic routing using sentence embeddings.

Routes prompts to triads based on cosine similarity of embeddings.
"""

import json
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from ._embedder import RouterEmbedder
from ._router_paths import DEFAULT_PATHS


class RoutingDecision(Enum):
    """Routing decision types."""

    ROUTE_IMMEDIATELY = "route"
    LLM_FALLBACK_REQUIRED = "llm_fallback"


class TriadRoute:
    """
    Represents a triad route with pre-computed embedding.

    Attributes:
        name: Triad name
        description: Triad purpose description
        example_prompts: Example user prompts for this triad
        keywords: Keywords associated with this triad
        embedding: Pre-computed 384-dim embedding vector
    """

    def __init__(
        self,
        name: str,
        description: str,
        example_prompts: List[str],
        keywords: List[str],
        embedding: np.ndarray,
    ):
        """
        Initialize triad route.

        Args:
            name: Triad name
            description: Triad purpose
            example_prompts: Example user prompts
            keywords: Associated keywords
            embedding: Pre-computed embedding vector
        """
        self.name = name
        self.description = description
        self.example_prompts = example_prompts
        self.keywords = keywords
        self.embedding = embedding

    def __repr__(self) -> str:
        """String representation."""
        return f"TriadRoute(name={self.name})"


class SemanticRouter:
    """
    Semantic router using sentence embeddings.

    Routes user prompts to triads based on cosine similarity between
    prompt embedding and pre-computed triad route embeddings.
    """

    def __init__(
        self,
        embedder: RouterEmbedder,
        routes_path: Optional[Path] = None,
    ):
        """
        Initialize semantic router.

        Args:
            embedder: RouterEmbedder instance
            routes_path: Path to triad_routes.json.
                        Defaults to ~/.claude/router/triad_routes.json
        """
        if routes_path is None:
            routes_path = DEFAULT_PATHS.routes_file

        self.embedder = embedder
        self.routes: List[TriadRoute] = []

        # Load and pre-compute route embeddings
        self._load_routes(routes_path)

    def _load_routes(self, routes_path: Path) -> None:
        """
        Load routes from JSON and pre-compute embeddings.

        Args:
            routes_path: Path to triad_routes.json
        """
        with open(routes_path) as f:
            data = json.load(f)

        for route_data in data["routes"]:
            # Combine description + examples for richer embedding
            # This gives the model more context to understand the triad's purpose
            combined_text = (
                f"{route_data['description']} "
                + " ".join(route_data["example_prompts"])
            )

            # Pre-compute embedding (done once at initialization)
            embedding = self.embedder.embed(combined_text)

            route = TriadRoute(
                name=route_data["name"],
                description=route_data["description"],
                example_prompts=route_data["example_prompts"],
                keywords=route_data["keywords"],
                embedding=embedding,
            )
            self.routes.append(route)

    def route(self, prompt: str) -> List[Tuple[str, float]]:
        """
        Route prompt to triads using semantic similarity.

        Returns list of (triad_name, confidence_score) sorted by confidence descending.

        Performance target: <10ms P95

        Args:
            prompt: User prompt to route

        Returns:
            List of (triad_name, confidence) tuples sorted by confidence descending
        """
        # Embed user prompt
        prompt_embedding = self.embedder.embed(prompt)

        # Compute cosine similarity with all routes
        scores = []
        for route in self.routes:
            similarity = self._cosine_similarity(prompt_embedding, route.embedding)
            scores.append((route.name, float(similarity)))

        # Sort by confidence descending
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.

        Formula: cos(θ) = (a · b) / (||a|| * ||b||)

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity score (-1.0 to 1.0)
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        # Handle zero vectors
        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def is_ambiguous(
        self,
        scores: List[Tuple[str, float]],
        threshold: float = 0.10,
    ) -> bool:
        """
        Check if top scores are too close (ambiguous).

        Ambiguous if: (top_score - second_score) < threshold

        Args:
            scores: List of (triad_name, score) tuples sorted descending
            threshold: Minimum score gap to consider unambiguous (default: 0.10)

        Returns:
            True if ambiguous, False otherwise
        """
        if len(scores) < 2:
            return False

        top_score = scores[0][1]
        second_score = scores[1][1]

        score_gap = top_score - second_score

        return score_gap < threshold

    def threshold_check(
        self,
        scores: List[Tuple[str, float]],
        confidence_threshold: float = 0.70,
        ambiguity_threshold: float = 0.10,
    ) -> Tuple[RoutingDecision, List[Tuple[str, float]]]:
        """
        Determine if semantic routing is confident enough.

        Decision logic:
        - If top_score >= confidence_threshold AND not ambiguous:
          → ROUTE_IMMEDIATELY
        - Otherwise:
          → LLM_FALLBACK_REQUIRED

        Args:
            scores: List of (triad_name, score) tuples sorted descending
            confidence_threshold: Minimum confidence to route immediately (default: 0.70)
            ambiguity_threshold: Maximum gap to consider ambiguous (default: 0.10)

        Returns:
            Tuple of (decision, candidates)
            - decision: ROUTE_IMMEDIATELY or LLM_FALLBACK_REQUIRED
            - candidates: Top 3 candidates (for LLM if needed, else just top 1)
        """
        if not scores:
            return (RoutingDecision.LLM_FALLBACK_REQUIRED, [])

        top_score = scores[0][1]
        is_ambig = self.is_ambiguous(scores, ambiguity_threshold)

        # High confidence AND not ambiguous → route immediately
        if top_score >= confidence_threshold and not is_ambig:
            return (RoutingDecision.ROUTE_IMMEDIATELY, scores[:1])

        # Low confidence OR ambiguous → LLM fallback
        # Return top 3 for LLM to disambiguate
        return (RoutingDecision.LLM_FALLBACK_REQUIRED, scores[:3])

    def __repr__(self) -> str:
        """String representation."""
        return f"SemanticRouter(routes={len(self.routes)})"
