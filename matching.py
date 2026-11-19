"""Semantic matching between a user description and the reference dataset.

Scoring (see README):
1. Score each reference description with the cosine similarity between its
   normalized embedding and the user's normalized embedding (a dot product).
2. Score each specialty with the highest similarity among its descriptions.
"""
import csv
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).resolve().parent / "data"
CSV_PATH = DATA_DIR / "specialities.csv"
EMBEDDINGS_PATH = DATA_DIR / "symptom_descriptions_embeddings.npz"
REBUILD_HINT = "Run `uv run python scripts/build_embeddings.py` to rebuild them."


def cosine_similarity(reference_embeddings: np.ndarray, user_embeddings: np.ndarray) -> np.ndarray:
    """Return one similarity score per reference description.

    Both inputs are already L2-normalized, so the dot product equals the cosine.
    """
    return reference_embeddings @ user_embeddings  # shape (n_references,)


def load_reference_embeddings(
    expected_model: str | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Load reference vectors and their corresponding description IDs.

    If expected_model is given, check that the vectors were built with it:
    vectors from different models are not comparable.
    """
    if not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(f"Reference embeddings not found. {REBUILD_HINT}")

    with np.load(EMBEDDINGS_PATH, allow_pickle=False) as data:
        embeddings = data["embeddings"]
        description_ids = data["description_ids"]
        model_name = str(data["model_name"]) if "model_name" in data else None

    if expected_model is not None and model_name != expected_model:
        raise ValueError(
            f"Reference embeddings were built with {model_name!r}, "
            f"but the app uses {expected_model!r}. {REBUILD_HINT}"
        )
    if embeddings.ndim != 2 or description_ids.ndim != 1:
        raise ValueError("Expected a matrix of embeddings and a list of description IDs.")
    if embeddings.shape[0] != len(description_ids):
        raise ValueError(f"Each reference embedding must have one description ID. {REBUILD_HINT}")

    return embeddings, description_ids


def load_references() -> dict[str, dict]:
    """Return the reference CSV rows indexed by description_id."""
    with CSV_PATH.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    references = {row["description_id"]: row for row in rows}
    if len(references) != len(rows):
        raise ValueError("Reference description IDs must be unique.")
    return references


def best_match_per_specialty(
    scores: np.ndarray,
    description_ids: np.ndarray,
    references: dict[str, dict] | None = None,
) -> list[dict]:
    """Return each specialty's strongest reference match, joined by description ID.

    Each match contains every CSV field (specialty_id, specialty, description_id,
    symptom_description, source_url, ...) plus a float "score".
    """
    if scores.ndim != 1 or description_ids.ndim != 1:
        raise ValueError("Scores and description IDs must be one-dimensional.")
    if len(scores) != len(description_ids) or not np.isfinite(scores).all():
        raise ValueError("Provide one finite score per description ID.")

    if references is None:
        references = load_references()

    best_matches = {}
    for description_id, score in zip(description_ids, scores):
        description_id = str(description_id)
        if description_id not in references:
            raise ValueError(f"Unknown reference description ID: {description_id}. {REBUILD_HINT}")
        reference = references[description_id]
        specialty_id = reference["specialty_id"]
        if specialty_id not in best_matches or score > best_matches[specialty_id]["score"]:
            best_matches[specialty_id] = {**reference, "score": float(score)}

    return list(best_matches.values())


def rank_specialties(text_to_embed: str) -> list[dict]:
    """Embed the prepared user text and return every specialty, best score first.

    This is the single entry point for the interface and the LLM explanations;
    callers take the top k with rank_specialties(text)[:k].
    """
    from embedding import MODEL_NAME, embed  # loads the model on first use

    user_embedding = embed(text_to_embed)
    reference_embeddings, description_ids = load_reference_embeddings(MODEL_NAME)
    scores = cosine_similarity(reference_embeddings, user_embedding)
    matches = best_match_per_specialty(scores, description_ids)
    return sorted(matches, key=lambda match: match["score"], reverse=True)
