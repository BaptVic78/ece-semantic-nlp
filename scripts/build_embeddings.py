# We choosed sentence-transformers/all-MiniLM-L6-v2 for embedding. It handles English sentences and short 
# paragraphs and produces 384-dimensional embeddings for semantic search. That makes it a suitable baseline
# for our symptom descriptions --> 45 symptom descriptions produce an array of (45, 384).

from pathlib import Path
import csv

import numpy as np
from sentence_transformers import SentenceTransformer

# This model produces one 384-dimensional vector per description.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "specialities.csv"
OUTPUT_PATH = DATA_DIR / "symptom_descriptions_embeddings.npz"


def embed_symptom_descriptions(descriptions: list[str]) -> np.ndarray:
    model = SentenceTransformer(MODEL_NAME)
    return model.encode(
        descriptions,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )


def main():
    with CSV_PATH.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    descriptions = [row["symptom_description"] for row in rows]
    description_ids = [row["description_id"] for row in rows]

    embeddings = embed_symptom_descriptions(descriptions)

    np.savez(
        OUTPUT_PATH,
        embeddings=embeddings,
        description_ids=description_ids,
        model_name=MODEL_NAME,
    )

    print(f"Saved embeddings to {OUTPUT_PATH}")
    print(embeddings.shape)     # (45, 384)
    print(embeddings[0].shape)  # (384,)


if __name__ == "__main__":
    main()