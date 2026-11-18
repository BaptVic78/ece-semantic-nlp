# Semantic analysis and contextual recommendation

Build a web questionnaire that compares free-text answers with a structured reference dataset. The reference application matches competencies to job profiles.

Document the embedding model, affinity score and evidence behind each recommendation.

## Selected theme

Medical specialty orientation based on symptom descriptions. Use fictional input and authoritative, non-personal medical references. The app currently previews questionnaire responses in memory.

## Run locally

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Next milestone

Populate data/specialties.csv with sourced reference descriptions. The brief recommends at least 40 descriptions and 15 specialties. Encode the descriptions and questionnaire text, compare them using cosine similarity, and rank specialties with an explanation linked to the matching reference. Document and evaluate the scoring rule using fictional cases.
