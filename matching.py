import csv
from pathlib import Path

import numpy as np

# this function returns one simimarity score by symptom description
def cosine_similarity(reference_embeddings: np.ndarray, user_embeddings: np.ndarray) -> np.ndarray:
    return reference_embeddings @ user_embeddings # shape (45,)

def load_reference_embeddings() -> tuple[np.ndarray, np.ndarray]:
    """Load reference vectors and their corresponding description IDs."""
    embeddings_path = (
        Path(__file__).resolve().parent
        / "data"
        / "symptom_descriptions_embeddings.npz"
    )
    with np.load(embeddings_path, allow_pickle=False) as data:
        embeddings = data["embeddings"]
        description_ids = data["description_ids"]

    if embeddings.ndim != 2 or description_ids.ndim != 1:
        raise ValueError("Expected a matrix of embeddings and a list of description IDs.")
    if embeddings.shape[0] != len(description_ids):
        raise ValueError("Each reference embedding must have one description ID.")

    return embeddings, description_ids


def best_match_per_specialty(
    scores: np.ndarray,
    description_ids: np.ndarray,
) -> list[dict]:
    """Return each specialty's strongest reference match, joined by description ID."""
    if scores.ndim != 1 or description_ids.ndim != 1:
        raise ValueError("Scores and description IDs must be one-dimensional.")
    if len(scores) != len(description_ids) or not np.isfinite(scores).all():
        raise ValueError("Provide one finite score per description ID.")

    csv_path = Path(__file__).resolve().parent / "data" / "specialities.csv"
    with csv_path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    references = {row["description_id"]: row for row in rows}
    if len(references) != len(rows):
        raise ValueError("Reference description IDs must be unique.")

    best_matches = {}
    for description_id, score in zip(description_ids, scores):
        if description_id not in references:
            raise ValueError(f"Unknown reference description ID: {description_id}")
        reference = references[description_id]
        specialty_id = reference["specialty_id"]
        if specialty_id not in best_matches or score > best_matches[specialty_id]["score"]:
            best_matches[specialty_id] = {**reference, "score": float(score)}

    return list(best_matches.values())
