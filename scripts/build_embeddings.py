"""Build the reference cache from the corpus and the shared encoder."""
import argparse
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from embedding import MODEL_NAME, embed
from matching import BASELINE_CACHE_PATH, BASELINE_CSV_PATH, CACHE_PATH, CSV_PATH, read_references


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true", help="Build the original 45-row cache.")
    args = parser.parse_args()
    csv_path, cache_path = (BASELINE_CSV_PATH, BASELINE_CACHE_PATH) if args.baseline else (CSV_PATH, CACHE_PATH)
    rows, fingerprint = read_references(csv_path)
    vectors = embed([row["symptom_description"] for row in rows])
    with NamedTemporaryFile(dir=cache_path.parent, suffix=".npz", delete=False) as file:
        temporary = Path(file.name)
    try:
        np.savez(temporary, embeddings=vectors,
                 description_ids=[row["description_id"] for row in rows],
                 model_name=MODEL_NAME, fingerprint=fingerprint)
        temporary.replace(cache_path)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"Saved {vectors.shape} to {cache_path}")


if __name__ == "__main__":
    main()
