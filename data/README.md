# Reference dataset

`specialities_210.csv` is the application corpus, with 14 English descriptions per specialty. Its first 45 rows reproduce the baseline exactly, and the other 165 rows include their own source URLs and publishers. `specialities.csv` remains the baseline documented below.

specialities.csv contains 45 English source-based paraphrases, covering three distinct conditions and symptom patterns for each of 15 specialty categories. Each row links to its NHS reference. Descriptions summarize possible symptoms; symptoms in a row are not necessarily present together in every case.

## Columns and retrieval

Each description_id identifies one reference. specialty_id is the grouping key. symptom_category describes the symptom pattern. source_condition identifies the source topic and is metadata, not a predicted diagnosis. source_url supports the paraphrase. accessed_date records source access, not the medical review date.

Embed symptom_description only. Keep specialty names and source_condition out of the embedding text so retrieval reflects symptom meaning. Display the retrieved description as a paraphrase with its source link. Rebuild cached embeddings whenever this CSV changes.

## Scope and provenance

NHS public reference pages supplied symptom information. Specialty labels are educational dataset assignments based on the organ system and specialty scope. They are not NHS referral instructions or clinically validated ground truth. Primary care commonly evaluates these symptoms first. Other specialties may also be relevant, especially for overlapping urinary, neurological, allergic and endocrine symptoms. Nephrology includes one explicitly pediatric reference; the category includes pediatric nephrology.

The data contain no patient records, treatment instructions or urgency labels. The dataset is designed for a classroom semantic retrieval demonstration. It does not provide exhaustive specialty coverage. Independent fictional queries are required to measure retrieval accuracy, including ambiguous and out-of-domain queries. Measured classroom retrieval results are provided in ../evaluation/results.json. The corpus has no clinical validation.

Descriptions were paraphrased from individually inspected pages. Automated checks covered required values, unique identifiers and descriptions, and three distinct conditions and symptom categories per specialty. Source URLs were checked during construction. No review_status column is used.

The local audit on 19 November 2026 reached all 45 NHS pages (HTTP 200) and compared the paraphrases with the source symptom sections. Two descriptions were tightened for source fidelity. See source_audit.csv for the row-level record. Specialty labels remain project assignments.


