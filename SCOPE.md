# Medical specialty orientation | v1 scope

Build a local, English-language Streamlit classroom demo. A student enters a fictional symptom description and sees which medical specialty reference descriptions are closest in meaning.

## Reference data

The group will curate 45 distinct descriptions, three per specialty, from authoritative public hospital, medical society or public health sources. Record the supporting URL, specialty, symptom category and a faithful paraphrase in each row. A group member checks that each source supports both the wording and the specialty association. Use only public, non-personal reference material.

The 15 categories are dermatology, ophthalmology, otolaryngology (ENT), cardiology, pulmonology, gastroenterology, neurology, rheumatology, orthopedics, urology, nephrology, endocrinology, gynecology, allergy and immunology, and hematology. A description may overlap specialties.

## User flow and scoring

Collect free text plus location, duration and reported intensity. Preview the structured response in memory. Compare the description and any supplied location to reference descriptions using a pretrained English sentence embedding model and cosine similarity. Show duration and intensity as context only.

For each specialty, take its highest reference similarity, then display the top three specialties in descending order. This rule lets a single specific description support a match. For each result show the raw similarity, matched passage, source link and a template explanation. Add a bar chart comparing scores. Label scores as text similarity. Display the educational disclaimer before input and alongside results.

## Boundaries

Use fictional questionnaire responses. Exclude patient records, diagnosis, treatment, urgency decisions, accounts, deployment, chatbots and agents from v1.

## Completion criteria

- Run the local questionnaire end to end with the reviewed CSV and document installation and model setup.
- Evaluate 15 fictional cases written separately from the reference descriptions, one intended specialty per case. Record expected specialties before running the model, report top-three hit count, and discuss ambiguous or missed matches. This evaluates retrieval for the class demo.
- Deliver commented code, PDF documentation covering sources, preprocessing, scoring choices, evaluation and limitations, and an in-class presentation and working demo.

## Agreed LLM extension

Add grounded explanations of the ranked specialties using the user input, retrieved descriptions, scores and source URLs as context. This is a simple RAG extension built on the existing retrieval engine. Preserve the calculated ranking and provide a template fallback if the LLM is unavailable. Axel owns this extension, with Thomas integrating the explanations into the interface. See TEAM.md for the full allocation.
