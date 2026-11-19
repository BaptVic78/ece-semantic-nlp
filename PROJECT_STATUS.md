# Project status

- Delivered locally: Streamlit application, 45-row source audit, frozen case set, evaluation script and results, English PDF and editable report sources. See README.md for PowerShell setup.
- Corpus: 45 unique references across 15 specialties. All 45 NHS URLs returned HTTP 200 on 19 November 2026. Two paraphrases were tightened based on the source wording. See data/source_audit.csv.
- Evaluation: 22 fixed fictional prompts. Top 1: 13/15 (86.7%). Top 3: 15/15 (100%). Both intended labels appeared in the top three in all three ambiguous cases. Vague and unrelated inputs still return three ranks. See evaluation/results.json.
- Verified: locked dependency installation, MiniLM offline embedding build and evaluation, five unit tests, missing-cache handling, and Edge runs with template and live explanations. Qwen3 8B produced validated evidence for the demonstrated result with Ollama reporting 100% GPU, 5.3 GB and a 2,048-token context.
- Limits: the measurements describe the fictional test set, and clinical performance was not evaluated. Qwen3 forced CPU mode is documented and was not benchmarked. Remaining course work: presentation, outside this delivery.
- Report QA: rendered and visually inspected all eight A4 pages. Confirmed the PDF counts and saved case and corpus fingerprints agree. The report includes the actual Edge capture of the live Qwen result.

## Expanded reference corpus

- Created data/specialities_210.csv as a separate corpus, preserving the original 45 rows byte for byte and adding 165 English descriptions with source links. Validated 210 unique IDs and descriptions, exactly 14 rows for each of 15 specialties, and no empty fields.
- MiniLM encoded all 210 rows. For the exploratory vomiting, fever and dry cough case, the 45-row ranking started with Urology (0.483), while the 210-row ranking started with Pulmonology (0.640). The wider corpus has yet to undergo a comparative evaluation on fresh cases.
- The original measured evaluation uses the 45-row corpus.

- Compared the 45- and 210-row corpora with identical MiniLM cosine/max ranking. On 15 original single-label cases: 45 rows 13/15 top 1 and 15/15 top 3; 210 rows 14/15 top 1 and 14/15 top 3. On 30 new single-label cases fixed before retrieval: 45 rows 22/30 top 1 and 26/30 top 3; 210 rows 26/30 top 1 and 30/30 top 3. The new set was designed to probe coverage after both corpora were known.
- Comparative cases, scores and reproducer: evaluation/comparison_cases.csv, evaluation/corpus_comparison.json and scripts/compare_corpora.py.
- The application now defaults to the 210-row corpus with its own embedding cache. The original corpus, cache, evaluation and report are retained as a reproducible baseline.
- Verified the expanded default in Edge with Streamlit and three source links. The fictional cough, fever and vomiting example now ranks Pulmonology first. Five unit tests passed, and the original cache still matches the historical evaluation fingerprint.
- Refreshed the Streamlit theme and removed the repeated information banners. Verified the new form and ranked results in Edge at desktop and 390px mobile widths, including empty-input handling and source links.
- Updated the English report in report/. It documents the current 210-row application, the 45/210 comparison and its limits, and includes a current Streamlit screenshot. All six pages were rendered and inspected. The baseline report remains in output/pdf/.
