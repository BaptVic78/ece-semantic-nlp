"""Editable prose for the current project report."""

SECTIONS = [
    {
        "label": "Corpus and project scope",
        "title": "Medical Specialty Finder",
        "lead": "A small experiment in matching symptom descriptions to published references.",
        "paragraphs": [
            "The project started with a simple question. If two people describe the same symptoms in different words, can a sentence model still find a useful reference passage? We built a local Streamlit application to test that idea. It takes a short description in English and shows the three specialty categories whose reference passages score highest.",
            "The first version used 45 passages, three for each of 15 specialties. That was enough to see whether the pipeline worked, but the results could be fragile. A passage could move to the top because it matched one symptom while saying something quite different about the rest of the case. We kept all 45 entries and added 165, bringing each specialty to 14 descriptions. The application now uses this larger corpus.",
            "The descriptions are English paraphrases of public patient information. Most come from the NHS [1], with several additional entries based on pages from public health institutes or medical organisations. Each row keeps its original URL and publisher. The specialty labels were assigned for this project. A source supports the symptom wording, while the label records how that passage was grouped in the dataset.",
            "There are 210 descriptions and 201 distinct source URLs. Some pages support more than one symptom pattern. This is a collection of reference text, with no patient records. The results measure how closely texts match. They do not establish a diagnosis or provide a medical referral.",
        ],
    },
    {
        "label": "Retrieval method",
        "title": "How the ranking works",
        "paragraphs": [
            "The app accepts a symptom description, an optional body area, an optional duration and a reported intensity. It tidies spaces in the first two fields before encoding them together. Duration and the intensity dropdown are displayed with the result. They have no effect on the score, although time or intensity mentioned in the free text can influence the encoding.",
            "We use all-MiniLM-L6-v2 [2] to turn each passage into a vector of 384 numbers. The same model encodes the query. Only the symptom description goes into each reference vector. The title of the source page and the specialty name are kept as metadata, so the comparison is driven by the wording of the passage.",
            "Cosine similarity measures how closely the vectors point in the same direction. Since the encoder normalises both vectors to length one, the score is simply their dot product. This gives one score per passage. The highest score within each specialty becomes that specialty's score. The app sorts the 15 scores and shows the first three, with the passage responsible for each one.",
            "Taking the maximum makes the result easy to trace to a source. It also gives an unrelated passage a chance to win if a prominent detail happens to match. Giving every specialty 14 passages keeps the corpus balanced in size, although it cannot make the coverage of the specialties equally complete.",
            "Reference vectors are computed once and stored locally. The app checks the model name, file fingerprint, description IDs and shape before using the saved vectors. If the CSV has changed, the cache must be rebuilt.",
        ],
    },
    {
        "label": "Results screen",
        "title": "Reading a result",
        "paragraphs": [
            'The figure shows what the current app displays for the test sentence "I am vomiting, I have a fever, and I have a dry cough." The first card links to the source of the passage that mentions coughing and fever. The same source is shown beside the result regardless of which explanation is available.',
        ],
        "after": [
            'When Ollama is available, the app passes the query and its three retrieved passages to Qwen3 8B [3, 4]. Qwen3 proposes short quotes from the query and reference for the "Matching excerpts" section. The app checks that both quotes appear in their respective texts. If it cannot use a pair, "About this match" displays a standard note. The figure shows that fallback.',
            "This is the project's retrieval-augmented explanation step. MiniLM fixes the ranking before Qwen3 is called. A copied excerpt can show why two texts have something in common, but it can still leave out important differences between them.",
        ],
    },
    {
        "label": "Evaluation",
        "title": "Comparing 45 and 210 passages",
        "paragraphs": [
            "Both corpora were run through the same model and scoring code. We used the 15 single-target cases from the first report and 30 additional cases, two per specialty. We recorded a single expected specialty for each before running either corpus. A top-one hit means it was ranked first. A top-three hit means it was among the three shown in the app.",
        ],
        "after": [
            "On the original set, the larger corpus gained one first-place hit and lost one top-three hit. On the new set, six cases gained a correct first-place result and two lost one. Four cases became top-three hits and none dropped out of the top three. In a separate check, both corpora returned both anticipated labels in all seven ambiguous cases.",
            "The new cases were written after the topics of both corpora were known. Some deliberately probe situations that the expansion was meant to cover. This is a useful check on coverage, but it gives the larger corpus a favourable test and leaves the result on independently written cases open. The unrelated prompts were kept separate: both corpora still returned three categories for them.",
            "We chose 210 passages for the current app because it covered more of the new examples. The original corpus and its results remain available for comparison. There is no clinical performance estimate from either test.",
        ],
    },
    {
        "label": "Case review",
        "title": "What improved, what still goes wrong",
        "paragraphs": [
            "In the original corpus, the cough, fever and vomiting example put Urology first (0.483) and Pulmonology second (0.478). The Urology passage mentioned vomiting, but it was mainly about pain in the side and lower back, which the query never mentioned. With the expanded corpus, a passage that mentions both cough and fever placed Pulmonology first (0.640). This query had no single expected label, so it was kept out of the accuracy counts.",
            "The effect is easier to judge when a case has an intended label. In N18 the first steps after getting out of bed hurt beneath the heel. The 45-passage corpus did not show Orthopedics in the first three. The expanded corpus found a heel-pain passage with the same timing and put Orthopedics first (0.751).",
            "The larger corpus also has more opportunities to retrieve a superficial match. In S12, thirst, frequent trips to the toilet and looser clothes were intended to point to Endocrinology. The original corpus placed it second. Urology kept the same top score in the larger corpus, while new Cardiology and Nephrology passages moved ahead of Endocrinology and pushed it out of the top three.",
            "A second group member could write a fresh set of cases without reading the CSVs. That would help tell whether remaining misses come from gaps in the data or from the scoring rule. A separate question is when the app should abstain. At present a request about merging spreadsheet cells still produces specialty cards, even though the query has no relevant symptoms.",
        ],
    },
    {
        "label": "Reproduction and sources",
        "title": "Running the project",
        "paragraphs": [
            "The project runs locally with Python, uv and Streamlit. The first setup downloads the locked dependencies and MiniLM weights. Once the weights are cached, retrieval can run offline. Ollama is optional for explanations. The app sends requests to the local Ollama endpoint, and each source link opens the publisher's page in the browser.",
            "The application and the test sets are in English. French input can be entered, but retrieval quality in French was not measured. The benchmark concerns specialty ranking, so it does not measure the usefulness of Qwen3's quotes.",
        ],
    },
]
