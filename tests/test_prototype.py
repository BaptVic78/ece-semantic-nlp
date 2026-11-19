import csv
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np

import explanations
from input_processing import prepare_input
import matching


class PrototypeTests(unittest.TestCase):
    def test_input(self):
        self.assertEqual(prepare_input("  dry   skin ", " arms "), "Symptoms: dry skin\nLocation: arms")
        with self.assertRaises(ValueError):
            prepare_input("   ", "arms")

    def test_reference_integrity(self):
        rows, _ = matching.read_references()
        baseline, _ = matching.read_references(matching.BASELINE_CSV_PATH)
        self.assertEqual(len(baseline), 45)
        self.assertEqual(rows[:45], baseline)
        self.assertEqual(len(rows), 210)
        self.assertEqual(len({r["symptom_description"] for r in rows}), 210)
        counts = Counter(r["specialty_id"] for r in rows)
        self.assertEqual(len(counts), 15)
        self.assertEqual(set(counts.values()), {14})
        for r in rows:
            self.assertTrue(all(v and v.strip() for v in r.values()))
            self.assertTrue(r["source_url"].startswith("https://"))
        with Path("data/source_audit.csv").open(encoding="utf-8", newline="") as file:
            audit = list(csv.DictReader(file))
        self.assertEqual({r["description_id"] for r in audit}, {r["description_id"] for r in baseline})

    def test_cache_accepts_aligned_data_and_rejects_bad_data(self):
        rows = [{"description_id": "A"}, {"description_id": "B"}]
        vectors = np.eye(2, matching.DIMENSIONS)
        metadata = dict(description_ids=["A", "B"], model_name=matching.MODEL_NAME,
                        fingerprint="original", embeddings=vectors)
        with TemporaryDirectory() as directory, patch.object(
            matching, "CACHE_PATH", Path(directory) / "cache.npz"
        ):
            with self.assertRaisesRegex(ValueError, "missing, outdated or incompatible"):
                matching.load_reference_embeddings(rows, "original")
            np.savez(matching.CACHE_PATH, **metadata)
            np.testing.assert_array_equal(matching.load_reference_embeddings(rows, "original"), vectors)
            for overrides in (
                {"description_ids": ["B", "A"]}, {"fingerprint": "old"},
                {"model_name": "stale"}, {"embeddings": vectors * 4},
                {"embeddings": vectors[:, :2]},
            ):
                with self.subTest(overrides=overrides):
                    np.savez(matching.CACHE_PATH, **(metadata | overrides))
                    with self.assertRaisesRegex(ValueError, "missing, outdated or incompatible"):
                        matching.load_reference_embeddings(rows, "original")

    def test_cosine_and_aggregation(self):
        vectors = np.array([[0, 1], [1, 0], [.6, .8], [-1, 0]])
        scores = matching.cosine_similarity(vectors, np.array([1, 0]))
        rows = [{"specialty_id": key, "description_id": str(i)}
                for i, key in enumerate(["A", "A", "B", "C"])]
        self.assertEqual([m["description_id"] for m in matching.best_match_per_specialty(scores, rows)],
                         ["1", "2", "3"])
        with self.assertRaises(ValueError):
            matching.best_match_per_specialty(np.array([0, 1, .6, np.nan]), rows)

    def test_explanations_preserve_rank_and_reject_invented_text(self):
        matches = [
            dict(description_id="D", specialty="Dermatology", score=.7,
                 symptom_description="Itchy skin develops."),
            dict(description_id="O", specialty="Ophthalmology", score=.2,
                 symptom_description="Eyes feel gritty."),
        ]
        with patch.object(explanations, "request_selections", return_value={
            "O": {"query": "rash", "reference": "wear glasses"},
            "D": {"query": "itchy skin", "reference": "Itchy skin"},
        }):
            notes = explanations.explain_matches("I have itchy skin and a rash.", matches)
        self.assertEqual([selected for _, selected in notes], [True, False])
        self.assertIn("Ophthalmology", notes[1][0])
        with patch.object(explanations, "request_selections", side_effect=TimeoutError):
            self.assertFalse(any(selected for _, selected in explanations.explain_matches("rash", matches)))


if __name__ == "__main__":
    unittest.main()

