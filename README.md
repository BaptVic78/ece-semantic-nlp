## Project description

An NLP web application that compares natural-language symptom descriptions with a structured reference dataset using sentence embeddings and cosine similarity to rank relevant medical specialties.

## Selected theme

Medical specialty orientation based on symptom descriptions. The dataset contains 45 English descriptions across 15 specialties, supported by NHS references. This educational prototype uses fictional inputs and does not provide diagnoses, treatment recommendations or urgency assessments.

## Prerequisites

- Python 3.12 or later
- uv
- Internet access for dependency installation and the first embedding model download

## Run locally

```bash
cd /home/victor/ece-semantic-nlp
uv sync
uv run python scripts/build_embeddings.py
uv run streamlit run app.py
```

## Scoring mechanism

2 steps : 
1. Score each reference description using cosine similarity between its embedding and the user's embedding.
2. Score each speciality using the highest similarity among its three descriptions.