"""Measure retrieval on the fixed set of fictional prompts."""
import csv
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from embedding import MODEL_NAME
from input_processing import prepare_input
from matching import BASELINE_CACHE_PATH, BASELINE_CSV_PATH, rank_specialties, read_references


def main():
    cases_path = ROOT / "evaluation" / "cases.csv"
    with cases_path.open(encoding="utf-8-sig", newline="") as file:
        cases = list(csv.DictReader(file))
    records = []
    for case in cases:
        expected = case["expected"].split("|") if case["expected"] else []
        matches = rank_specialties(
            prepare_input(case["description"], case["location"]),
            csv_path=BASELINE_CSV_PATH, cache_path=BASELINE_CACHE_PATH,
        )
        records.append({
            "id": case["id"], "group": case["group"], "expected": expected,
            "matches": [{k: match[k] for k in ("specialty_id", "description_id", "score")}
                        for match in matches],
        })

    single = [record for record in records if record["group"] == "single"]
    result = {
        "model": MODEL_NAME, "cases_sha256": sha256(cases_path.read_bytes()).hexdigest(),
        "corpus_sha256": read_references(BASELINE_CSV_PATH)[1], "single_target_count": len(single),
        "top_one_hits": sum(r["matches"][0]["specialty_id"] in r["expected"] for r in single),
        "top_three_hits": sum(any(m["specialty_id"] in r["expected"] for m in r["matches"]) for r in single),
        "records": records,
    }
    path = cases_path.with_name("results.json")
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    count = result["single_target_count"]
    print(f"Top 1: {result['top_one_hits']}/{count}; top 3: {result['top_three_hits']}/{count}")
    print(path)


if __name__ == "__main__":
    main()
