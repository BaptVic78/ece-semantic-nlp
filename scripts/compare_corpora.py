"""Compare the original and expanded corpora using the same retrieval rule."""
import csv
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from embedding import MODEL_NAME, embed
from input_processing import prepare_input
from matching import best_match_per_specialty, cosine_similarity


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def fingerprint(path):
    return sha256(path.read_bytes()).hexdigest()


def compare(cases, corpora, vectors):
    queries = embed([prepare_input(c["description"], c["location"]) for c in cases])
    records = []
    for case, query in zip(cases, queries):
        expected = case["expected"].split("|") if case["expected"] else []
        record = dict(id=case["id"], group=case["group"], expected=expected, rankings={})
        for label, rows in corpora.items():
            scores = cosine_similarity(vectors[:len(rows)], query)
            record["rankings"][label] = [
                {k: match[k] for k in ("specialty_id", "description_id", "score")}
                for match in best_match_per_specialty(scores, rows)[:3]
            ]
        records.append(record)
    single = [r for r in records if r["group"] == "single"]
    ambiguous = [r for r in records if r["group"] == "ambiguous"]
    summary = {}
    for label in corpora:
        def ids(record):
            return [m["specialty_id"] for m in record["rankings"][label]]
        summary[label] = dict(
            single_count=len(single),
            top_one=sum(ids(r)[0] in r["expected"] for r in single),
            top_three=sum(bool(set(ids(r)) & set(r["expected"])) for r in single),
            ambiguous_count=len(ambiguous),
            ambiguous_all_in_top_three=sum(set(r["expected"]).issubset(ids(r)) for r in ambiguous),
        )
    return dict(summary=summary, records=records)


def main():
    paths = {label: ROOT / "data" / filename for label, filename in (
        ("45", "specialities.csv"), ("210", "specialities_210.csv")
    )}
    sets = {label: ROOT / "evaluation" / filename for label, filename in (
        ("original", "cases.csv"), ("new", "comparison_cases.csv")
    )}
    corpora = {label: read_csv(path) for label, path in paths.items()}
    assert len(corpora["45"]) == 45 and len(corpora["210"]) == 210
    assert corpora["45"] == corpora["210"][:45]
    vectors = embed([row["symptom_description"] for row in corpora["210"]])
    output = {
        "embedding_model": MODEL_NAME,
        "corpus_sha256": {label: fingerprint(path) for label, path in paths.items()},
        "case_set_sha256": {label: fingerprint(path) for label, path in sets.items()},
        "evaluations": {
            label: compare(read_csv(path), corpora, vectors) for label, path in sets.items()
        },
    }
    path = ROOT / "evaluation" / "corpus_comparison.json"
    path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    for label, evaluation in output["evaluations"].items():
        print(label, evaluation["summary"])


if __name__ == "__main__":
    main()
