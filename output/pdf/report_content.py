"""Editable text for the English project report."""

PAGES = [
("01 / PROJECT OVERVIEW", "Medical specialty text matching", [
("A local NLP retrieval study", "A Streamlit questionnaire compares fictional English symptom descriptions with a small corpus of NHS-based reference passages. Each submission returns three specialty categories, their raw cosine scores and the passages that contributed those scores. The interface lets a reader inspect why a category appeared and follow the original source link."),
("Research question", "Can a compact pretrained sentence encoder retrieve the intended educational category from a short, independently worded description? We assess this with a fixed collection of fictional cases and distinguish retrieval success from medical usefulness."),
("Scope", "The project runs on one computer. It uses no patient records and provides no diagnosis, treatment recommendations or urgency assessment. The prototype uses an English-language corpus and asks that the demo inputs remain fictional."),
("Reading the results", "The rank expresses proximity to the texts that happen to be in the corpus. A close reference can help demonstrate semantic retrieval. Actual referral decisions require a different task definition, data and validation process."),
]),
("02 / CORPUS", "What the reference set covers", [
("Source construction", "The corpus consists of 45 English paraphrases from public NHS condition and symptom pages. Each row stores a stable description ID, category ID, specialty label, symptom pattern, source topic, URL, publisher and access date. Three distinct patterns per specialty provide a balanced classroom example."),
("What the labels mean", "The NHS pages support the symptom wording. The specialty labels are educational dataset assignments based on specialty scope. One row can describe a symptom pattern relevant to several services. The pediatric nephrotic-syndrome reference also makes the age context explicit."),
("Source audit", "On 19 November 2026 all 45 pages returned HTTP 200. The audit compared the symptom paraphrases with the page content, removed an unsupported frequency qualifier for blurred vision and replaced an unsupported viscosity qualifier with source-described nasal mucus colours. The row-level audit and URLs are in data/source_audit.csv."),
("What gets encoded", "Only symptom_description enters the reference encoder. Specialty names, condition labels, links and keywords are metadata. This avoids making the query match an explicit specialty name that a fictional respondent might happen to write."),
]),
("03 / RETRIEVAL", "From questionnaire to ranking", [
("Preparing the query", "The description is required. The input processor collapses whitespace, prefixes the description with Symptoms and appends the optional Location on a separate line. Duration and intensity remain outside the embedding and are shown as context."),
("Vector representation", "The shared sentence encoder is all-MiniLM-L6-v2. It maps short texts into 384-dimensional vectors. The corpus is represented by a 45 by 384 matrix, and each query is a single vector of the same width. The model is lazy-loaded once per process and the small workload uses CPU by default."),
("Scoring and aggregation", "The dot product equals cosine similarity because all vectors have unit length. Each specialty takes the maximum of its three reference scores. The winning passage is therefore the evidence for that category. Sorting by decreasing score gives the first three specialties. Equal specialty scores use the specialty ID to break ties."),
("Cache integrity", "The cache stores the embedding model name, a SHA-256 fingerprint of the corpus and the ordered description IDs. Loading checks all three together with the vector shape, finite values and unit norms. The build writes through a temporary file to avoid leaving a partial replacement."),
]),
("04 / INTERFACE", "Reading a submission", [
("Questionnaire", "The form requests a short English description and optional location and duration. The reported intensity field defaults to unspecified. The same educational message appears before the form and again at the end of the results."),
("Result display", "A horizontal chart compares the three cosine scores. Cards retain the ranking and show the raw score, the winning passage, an evidence note and a direct NHS link. Duration and intensity are visible as context only."),
("Recoverable errors", "An empty submission receives an inline prompt. A missing or stale embedding cache displays the rebuild command. A model or retrieval failure yields a short recovery message while technical details remain in the terminal."),
]),
("05 / LOCAL EXPLANATIONS", "Evidence selection with Qwen3", [
("Retrieval augmented explanation", "The app sends the query and the three retrieved descriptions, IDs, scores and URLs to Ollama on the local loopback interface. Qwen3 8B is used as a span selector. The ranker and the explanation step have separate roles: one decides the order and the other identifies text to compare."),
("Output constraints", "For each description ID the model may propose a short query quote and a short passage quote. The application checks that each string occurs in its corresponding input. A fixed template then labels the selected quotes. The interface supplies the original NHS link, independent of any generated output."),
("Fallback and limitations", "A missing valid pair, service failure, or explicit opt-out yields the same deterministic template for that rank. Copied wording establishes provenance of the selected span. Selection can still be unhelpful or miss a qualifier, so the full passage is displayed for context."),
("Deployment choice", "Qwen3 8B Q4_K_M weighs about 5.2 GB and uses the Apache 2.0 licence. The selected configuration keeps the prompt bounded with a 2,048-token context. Ollama can be forced onto CPU through the app configuration. The environment and validation record appear on page 8."),
]),
("06 / EVALUATION", "Fixed-case retrieval results", [
("Case design", "The evaluation contains 15 single-target prompts, with one intended category per specialty, plus three ambiguous cases, three unrelated prompts and one vague prompt. Labels were recorded before any retrieval run. Queries use everyday phrasing and were written separately from reference text. The cases were designed for coverage rather than random sampling."),
("Measurement", "The evaluation script invokes the exact retrieval function used in the app. Top-one counts the expected category at rank one. Top-three counts the expected category anywhere in the three returned categories. Ambiguous cases are inspected against both acceptable labels and do not enter either denominator."),
("Reproducibility", "Each saved record contains its expected label set, ordered specialties, reference IDs and unrounded scores. The result file also records the corpus and case fingerprints. There was no change to ranking or to case labels after inspecting the scores."),
]),
("07 / ERROR ANALYSIS", "Where the ranking breaks down", [
("Single-target errors", "S04 uses a figurative description of pressure during exertion. Neurology edged Cardiology by about 0.010, suggesting that the global representation did not make the exertional context decisive. In S12, frequent trips to the toilet placed Urology ahead of Endocrinology despite the combined clues of thirst and weight change."),
("Ambiguous inputs", "Both intended categories appear in all three top-three lists. A01 retrieves Pulmonology then Cardiology for breathlessness and chest tightness. A02 retrieves Nephrology then Urology for side pain and red urine. A03 retrieves Orthopedics then Rheumatology, with the second anticipated label, Neurology, at rank three."),
("Unrelated and vague inputs", "The three unrelated prompts still received top scores between 0.239 and 0.301. The vague input 'I just feel a bit off' reached 0.489, higher than the top score in the S04 chest case. These examples argue against deriving an abstention threshold from this small set."),
("Next experiment", "Increase the number of independently written prompts per category and collect judgments from multiple reviewers. Include several plausible labels where symptoms overlap. Compare max aggregation and a lexical baseline on a separate development set, then measure on held-out examples."),
]),
("08 / REPRODUCIBILITY", "Run and verify the project", [
("Windows environment", "Python 3.12 or later, uv, and an initial network connection are needed for setup. MiniLM and the reference cache are local after setup. Ollama is optional for running retrieval and must be running for model-selected evidence."),
("Measured environment", "The machine reports an NVIDIA RTX 5070 Ti Laptop GPU with 12,227 MiB VRAM and driver 621.01. MiniLM and the saved evaluation used CPU. Runtime checks for Ollama and the UI are reported below."),
("Interpretation", "The result set is a classroom-sized assessment of retrieval behavior. It offers no estimate of clinical accuracy or population-wide performance. The balanced category count does not correct for limited symptom coverage or overlapping labels."),
]),
]
