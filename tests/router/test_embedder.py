"""Tests for router embedder."""

import time

import numpy as np
import pytest

from src.triads.router.embedder import RouterEmbedder


class TestRouterEmbedder:
    """Test RouterEmbedder functionality."""

    @pytest.fixture
    def embedder(self):
        """Create embedder instance."""
        return RouterEmbedder()

    def test_initialization(self, embedder):
        """Test embedder initialization."""
        assert embedder.embedding_dim == 384
        assert embedder.model_name == "all-MiniLM-L6-v2"
        assert embedder.model is not None

    def test_embed_shape(self, embedder):
        """Test embedding output shape."""
        text = "Let's design the authentication system"
        embedding = embedder.embed(text)

        assert embedding.shape == (384,)
        assert isinstance(embedding, np.ndarray)

    def test_embed_different_texts(self, embedder):
        """Test different texts produce different embeddings."""
        text1 = "Let's design the authentication system"
        text2 = "Implement the OAuth2 flow"

        embedding1 = embedder.embed(text1)
        embedding2 = embedder.embed(text2)

        # Embeddings should be different
        assert not np.allclose(embedding1, embedding2)

    def test_embed_similar_texts(self, embedder):
        """Test similar texts produce similar embeddings."""
        text1 = "Design the authentication system"
        text2 = "Design the auth mechanism"

        embedding1 = embedder.embed(text1)
        embedding2 = embedder.embed(text2)

        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )

        # Should be quite similar (>0.7)
        assert similarity > 0.7

    def test_embed_empty_string(self, embedder):
        """Test embedding empty string."""
        embedding = embedder.embed("")

        assert embedding.shape == (384,)

    def test_embed_long_text(self, embedder):
        """Test embedding long text."""
        long_text = "word " * 1000  # 1000 words
        embedding = embedder.embed(long_text)

        assert embedding.shape == (384,)

    def test_embed_batch_shape(self, embedder):
        """Test batch embedding output shape."""
        texts = [
            "Let's design the authentication system",
            "Implement the OAuth2 flow",
            "Refactor the codebase",
        ]

        embeddings = embedder.embed_batch(texts)

        assert embeddings.shape == (3, 384)
        assert isinstance(embeddings, np.ndarray)

    def test_embed_batch_consistency(self, embedder):
        """Test batch embedding matches individual embeddings."""
        texts = [
            "Let's design the authentication system",
            "Implement the OAuth2 flow",
        ]

        # Get batch embeddings
        batch_embeddings = embedder.embed_batch(texts)

        # Get individual embeddings
        individual_embeddings = [embedder.embed(text) for text in texts]

        # Should be very close (allowing for some numerical differences in batch processing)
        for i, text in enumerate(texts):
            # Use higher tolerance for batch vs individual differences
            assert np.allclose(batch_embeddings[i], individual_embeddings[i], rtol=1e-4, atol=1e-5)

    def test_embed_performance(self, embedder):
        """Test embedding performance is reasonable (<25ms)."""
        text = "Let's design the authentication system for the web application"

        # Warm up (first call may be slower)
        embedder.embed(text)

        # Measure performance
        times = []
        for _ in range(10):
            start = time.perf_counter()
            embedder.embed(text)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        p95_time = sorted(times)[int(0.95 * len(times))]

        # Should be <25ms P95 (real-world performance on M1 Mac is ~15-20ms)
        assert p95_time < 25, f"P95 latency {p95_time:.2f}ms exceeds 25ms limit"

    def test_repr(self, embedder):
        """Test string representation."""
        repr_str = repr(embedder)

        assert "RouterEmbedder" in repr_str
        assert "all-MiniLM-L6-v2" in repr_str
        assert "384" in repr_str

    def test_custom_model_name(self):
        """Test initialization with custom model name."""
        embedder = RouterEmbedder(model_name="all-MiniLM-L6-v2")

        assert embedder.model_name == "all-MiniLM-L6-v2"
