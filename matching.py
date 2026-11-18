import numpy as np

# this function returns one simimarity score by symptom description
def cosine_similarity(reference_embeddings: np.ndarray, user_embeddings: np.ndarray) -> np.ndarray:
    return reference_embeddings @ user_embeddings # shape (45,)