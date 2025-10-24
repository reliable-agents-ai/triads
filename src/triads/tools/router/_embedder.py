"""
Text embedding for semantic routing.

Uses sentence-transformers for fast, high-quality embeddings.
"""

from typing import List

import numpy as np

# Type checking for sentence_transformers (installed as dependency)
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError(
        "sentence-transformers not installed. "
        "Install with: pip install sentence-transformers"
    )


class RouterEmbedder:
    """
    Text embedder for router semantic similarity.

    Uses all-MiniLM-L6-v2 model:
    - 384-dimensional embeddings
    - ~80MB model size
    - <10ms inference for typical prompts
    - Pretrained on 1B+ sentence pairs
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedder.

        Args:
            model_name: Sentence-transformers model name
                       (default: all-MiniLM-L6-v2)
        """
        # Model will be cached at ~/.cache/torch by sentence-transformers
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = 384
        self.model_name = model_name

    def embed(self, text: str) -> np.ndarray:
        """
        Embed text to 384-dimensional vector.

        Performance: <10ms for typical prompts

        Args:
            text: Text to embed

        Returns:
            384-dimensional numpy array
        """
        embedding = self.model.encode(text, convert_to_numpy=True)

        # Validate shape
        if embedding.shape != (self.embedding_dim,):
            raise ValueError(
                f"Expected {self.embedding_dim}-dim embedding, "
                f"got shape {embedding.shape}"
            )

        return embedding

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Embed multiple texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            (N, 384) numpy array where N is number of texts
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        # Validate shape
        expected_shape = (len(texts), self.embedding_dim)
        if embeddings.shape != expected_shape:
            raise ValueError(
                f"Expected shape {expected_shape}, got {embeddings.shape}"
            )

        return embeddings

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"RouterEmbedder("
            f"model={self.model_name}, "
            f"embedding_dim={self.embedding_dim}"
            f")"
        )
