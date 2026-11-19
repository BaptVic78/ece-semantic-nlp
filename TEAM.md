# Team handoff

This file preserves the original team plan. The current local implementation and measured results are recorded in PROJECT_STATUS.md. Remote collaboration and slides are outside this local delivery.

## Project and current progress

We are building an English-language Streamlit educational application that compares fictional symptom descriptions with sourced references and ranks medical specialties. The semantic pipeline and basic interface are implemented. LLM explanations are the agreed extension and remain to be built.

- The questionnaire collects description, location, duration and intensity. Description and location are embedded; duration and intensity appear in the summary.
- data/specialities.csv contains 45 English reference descriptions, three distinct symptom patterns per specialty across 15 specialties, with NHS source links.
- scripts/build_embeddings.py encodes the reference descriptions using sentence-transformers/all-MiniLM-L6-v2 and saves normalized vectors, description IDs and the model name in data/symptom_descriptions_embeddings.npz.
- embedding.py embeds the user input using the same model. Each vector has 384 dimensions.
- matching.py loads the references, computes cosine similarity through a dot product of normalized vectors, and retains the highest score per specialty. app.py sorts these matches and shows the top three with matched descriptions and source links.
- A fictional skin-symptom submission was checked end to end. A systematic independent retrieval evaluation remains to be completed. Similarity scores are not probabilities.
- Score charts, personalized explanations and the final report and presentation remain to be completed.

## Responsibilities

| Member | Responsibility | Deliverables |
| --- | --- | --- |
| Victor | Semantic engine | Maintain input processing, embedding generation, cosine similarity and specialty ranking. Explain the scoring formula and provide structured matches to the interface and LLM. |
| Nils | Dataset and evaluation | Improve reference coverage and source support. Build independent fictional test cases with expected specialties recorded before execution. Measure top-three hit rate and analyse ambiguous, failed and out-of-domain queries. Document sources and results. |
| Thomas | Interface and visualization | Improve the questionnaire and results display, add score comparison charts, present evidence and source links clearly, handle errors, and integrate Axel's explanations into the results page. |
| Axel | LLM and RAG explanations | Use the user input and retrieved matches as context for an LLM. Implement concise grounded explanations, a template fallback, and checks for unsupported claims. Document model setup and configuration. |

## Integration agreement

The existing retrieval output is a list of dictionaries containing specialty_id, specialty, description_id, symptom_description, source_url and score, along with the other CSV fields. The semantic engine selects and ranks the top three. Thomas consumes these matches for display. Axel consumes the same matches and the user text to explain the evidence behind each result. Preserve these field names when integrating changes.

RAG reuses our semantic retrieval and supplies its selected passages to the LLM. The LLM explains the existing scores and ranking using only the supplied evidence, with source attribution. It must not invent symptoms, diagnoses, treatment advice or urgency assessments. The application must still return recommendations when the LLM is unavailable. Axel and Thomas should agree on the explanation function and return format before integrating it.

## Run locally

```bash
uv sync
uv run python scripts/build_embeddings.py
uv run streamlit run app.py
```

Rebuild reference embeddings whenever the CSV or embedding model changes. Keep description IDs aligned with vectors. Embed symptom_description only for reference data.

## Collaboration and completion

Each member works on their own branch, makes commits under their own Git account and opens a pull request describing the changes and checks. Another member reviews it before merging. Everyone documents their own implementation and contributes to the PDF report, presentation and demo. Follow the course rules on AI assistance and ensure each member can explain the submitted work.

The initial evaluation target is 15 independent fictional cases, one intended specialty per case, supplemented by ambiguous and out-of-domain cases. These should use wording different from the reference descriptions. Record expected results before running the model and report measured results, including failures. Dataset labels are educational specialty associations and have not received clinical validation.

