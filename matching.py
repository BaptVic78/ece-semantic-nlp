"""Load and score the reference corpus."""
import csv
from hashlib import sha256
from io import StringIO
from pathlib import Path
from zipfile import BadZipFile

import numpy as np

from embedding import DIMENSIONS, MODEL_NAME, embed

DATA_DIR = Path(__file__).resolve().parent / "data"
BASELINE_CSV_PATH = DATA_DIR / "specialities.csv"
BASELINE_CACHE_PATH = DATA_DIR / "symptom_descriptions_embeddings.npz"
CSV_PATH = DATA_DIR / "specialities_210.csv"
CACHE_PATH = DATA_DIR / "symptom_descriptions_embeddings_210.npz"
REBUILD = "Run: uv run python scripts/build_embeddings.py"


def read_references(csv_path=None):
    """Read rows and fingerprint the same bytes used to parse them."""
    raw = (csv_path if csv_path is not None else CSV_PATH).read_bytes()
    rows = list(csv.DictReader(StringIO(raw.decode("utf-8-sig"), newline="")))
    if not rows or any(not all(row.get(k) for k in (
        "description_id", "specialty_id", "specialty", "symptom_description", "source_url"
    )) for row in rows):
        raise ValueError("Reference corpus is empty or missing required fields.")
    if len({row["description_id"] for row in rows}) != len(rows):
        raise ValueError("Reference description IDs must be unique.")
    return rows, sha256(raw).hexdigest()


def load_reference_embeddings(rows, fingerprint, cache_path=None):
    """Check model, corpus fingerprint, row order, dimensions and normalization."""
    try:
        with np.load(cache_path if cache_path is not None else CACHE_PATH, allow_pickle=False) as cache:
            vectors = cache["embeddings"]
            ids = cache["description_ids"]
            if (cache["model_name"].item() != MODEL_NAME
                or cache["fingerprint"].item() != fingerprint
                or not np.array_equal(ids, [row["description_id"] for row in rows])):
                raise ValueError("Cache metadata differs from the current corpus or model.")
            if (vectors.shape != (len(rows), DIMENSIONS)
                or not np.issubdtype(vectors.dtype, np.floating)
                or not np.isfinite(vectors).all()
                or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-4)):
                raise ValueError("Cache contains invalid reference vectors.")
    except (OSError, KeyError, ValueError, TypeError, EOFError, BadZipFile) as error:
        rebuild = f"{REBUILD} --baseline" if cache_path == BASELINE_CACHE_PATH else REBUILD
        raise ValueError(f"Reference embeddings are missing, outdated or incompatible. {rebuild}") from error
    return vectors


def cosine_similarity(reference_embeddings, user_embedding):
    """Dot products equal cosine similarities for unit-normalized vectors."""
    return reference_embeddings @ user_embedding


def best_match_per_specialty(scores, rows):
    """Select the strongest passage per specialty, then rank the winners."""
    if scores.shape != (len(rows),) or not np.isfinite(scores).all():
        raise ValueError("Provide one finite score per reference.")
    best = {}
    for row, score in zip(rows, scores):
        key = row["specialty_id"]
        if key not in best or score > best[key]["score"]:
            best[key] = {**row, "score": float(score)}
    return sorted(best.values(), key=lambda match: (-match["score"], match["specialty_id"]))


def rank_specialties(text, *, csv_path=None, cache_path=None):
    """Use this same entry point in the demo and evaluation."""
    rows, fingerprint = read_references(csv_path)
    vectors = load_reference_embeddings(rows, fingerprint, cache_path)
    query = embed(text)
    if query.shape != (DIMENSIONS,) or not np.isclose(np.linalg.norm(query), 1, atol=1e-4):
        raise ValueError("The query encoder returned an invalid embedding.")
    return best_match_per_specialty(cosine_similarity(vectors, query), rows)[:3]

