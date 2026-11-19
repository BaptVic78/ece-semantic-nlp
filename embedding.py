"""Shared, lazily loaded sentence encoder for references and queries."""
from functools import lru_cache
import os

import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DIMENSIONS = 384


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME, device=os.getenv("EMBEDDING_DEVICE", "cpu"))


def embed(text: str | list[str]) -> np.ndarray:
    """Encode one string or a batch as unit-normalized vectors."""
    return _model().encode(text, normalize_embeddings=True, convert_to_numpy=True)
