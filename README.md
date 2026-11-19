## Project description

An NLP web application that compares natural-language symptom descriptions with a structured reference dataset using sentence embeddings and cosine similarity to rank relevant medical specialties.

## Selected theme

Medical specialty orientation based on symptom descriptions. The dataset contains 45 English descriptions across 15 specialties, supported by NHS references. This educational prototype uses fictional inputs and does not provide diagnoses, treatment recommendations or urgency assessments.

## Prerequisites

- Python 3.12 or later
- uv
- Internet access for dependency installation and the first embedding model download

## Run locally

From the repository root:

```bash
uv sync
uv run python scripts/build_embeddings.py
uv run streamlit run app.py
```

`data/symptom_descriptions_embeddings.npz` is generated, not committed. Rebuild it whenever `data/specialities.csv` or the embedding model changes; the app refuses embeddings built with another model.

## Scoring mechanism

2 steps : 
1. Score each reference description using cosine similarity between its embedding and the user's embedding.
2. Score each speciality using the highest similarity among its three descriptions.

`matching.rank_specialties(text)` runs both steps and returns every specialty sorted by score. Each match keeps the CSV fields (`specialty_id`, `specialty`, `description_id`, `symptom_description`, `source_url`, ...) plus `score`.

## Interface

- `app.py`: questionnaire (description and location are embedded; duration and intensity are context only), then the top three specialties as cards with the score, the matched reference paraphrase, source metadata, an explanation and the source link. The disclaimer is shown before the form and above the results.
- `visualization.py`: horizontal bar chart of the best score of all 15 specialties, top three highlighted. Scores are labelled as text similarity, not probabilities.
- If the best score is below `LOW_SIMILARITY_THRESHOLD` (0.30 in `app.py`, provisional until the evaluation calibrates it), the app warns that the query may be out of scope but still shows the matches.
- Missing or inconsistent embeddings produce an error message telling the user how to rebuild them.

## Explanation contract (LLM extension)

`explanations.explain_matches(user_input, matches)` returns, for each `specialty_id`, `{"text", "source": "llm" | "template", "cited_description_ids"}`. It never raises: a deterministic template explanation is used whenever the LLM is unavailable or fails. The LLM part lives in `generate_llm_explanations`, currently a documented stub; the app shows a badge saying whether each explanation is template or AI-generated.