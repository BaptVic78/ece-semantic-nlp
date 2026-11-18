from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
model = SentenceTransformer(MODEL_NAME)

def embed(input_text: str) -> np.ndarray:
    return model.encode(
        input_text,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    