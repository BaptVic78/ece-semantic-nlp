# Medical specialty text matching

A local Streamlit demonstration of sentence retrieval for fictional English symptom descriptions. It compares their wording with 210 sourced paraphrases, 14 for each of 15 educational specialty categories. The ranking describes similarity between texts. It provides no diagnosis, treatment guidance, urgency assessment or medical probability.

## Windows setup

From the project folder in PowerShell, with Python 3.12 or later and uv installed:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
$env:HF_HOME = Join-Path (Get-Location) '.hf-cache'
uv sync --locked
uv run --no-sync python scripts/build_embeddings.py
```

The first setup downloads dependencies and the [MiniLM model](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). Regenerate the reference embeddings whenever the corpus or embedding model changes. Once the model is cached, the following commands work offline in that same shell:

```powershell
$env:HF_HUB_OFFLINE = '1'
uv run --no-sync streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Use only fictional examples. Duration and intensity are displayed as context. Ranking uses normalized embeddings of the description and optional location, scores references by cosine similarity, then takes the strongest reference per specialty. Each result includes the matched passage, its score and a link to its source.

## Local explanations

The app defaults to [Qwen3 8B](https://ollama.com/library/qwen3:8b), an Apache-2.0 model distributed by Ollama as a 5.2 GB Q4_K_M quantization. The model selects short quotes from the submitted text and retrieved passages. The app checks the quotes against the original strings and formats the explanation in the existing rank order. It uses a deterministic explanation if no valid quote pair is available.

Install or open [Ollama for Windows](https://docs.ollama.com/windows), then run these commands to get the model, if needed, and check placement after inference:

```powershell
ollama pull qwen3:8b
ollama list
ollama ps
```

The app calls the [Ollama generate API](https://docs.ollama.com/api/generate) over loopback at 127.0.0.1:11434. It uses no external inference endpoint or API key. Ollama's existing model cache is normally under `$env:USERPROFILE\.ollama\models` on Windows. The project keeps uv and MiniLM caches in the workspace with the setup above. A 12 GB NVIDIA GPU has room for the selected weights plus runtime overhead under ordinary load. Check actual placement and available memory with `ollama ps` and `nvidia-smi`.

To force CPU inference for explanations, set `$env:LOCAL_LLM_CPU = '1'` before starting Streamlit. To change models, use `$env:LOCAL_LLM_MODEL = 'another-local-tag'`. To explicitly use template mode, set `$env:LOCAL_LLM_MODEL = 'off'`. The embedding model uses CPU by default. `EMBEDDING_DEVICE=cuda` requires a CUDA-enabled PyTorch environment, which is optional for this small corpus.

## Evaluation and report

```powershell
uv run --no-sync python -m unittest discover -s tests -v
uv run --no-sync python scripts/build_embeddings.py --baseline
uv run --no-sync python scripts/evaluate.py
uv run --no-sync python scripts/compare_corpora.py
```

The baseline build and `evaluate.py` reproduce the original 45-reference experiment with a separate cache and write `evaluation/results.json`. The current app uses `data/specialities_210.csv`. To compare both versions, run `compare_corpora.py`, which writes `evaluation/corpus_comparison.json`. On the 30 new single-target cases, the 210-reference version achieved 26/30 top-one and 30/30 top-three hits, against 22/30 and 26/30 with 45 references. These cases were designed with knowledge of both corpora.

Open [the current report](report/semantic-specialty-report.pdf) for the application and corpus comparison. Edit `report/report_content.py` to revise the prose. The original report is archived in `output/pdf/`.

```powershell
uv run --no-sync --with reportlab python report/build_report.py
```

## Troubleshooting

- **Reference cache missing or stale:** run the build command again after setting the same `HF_HOME`.
- **Encoder unavailable offline:** unset `HF_HUB_OFFLINE` for the first download, rebuild once, and restore offline mode.
- **Template explanations only:** check Ollama and `ollama list`. Individual results may also use the template when no valid quote is returned.
- **Model slow or memory constrained:** close other GPU-heavy applications or use template mode. The first Ollama request can take longer while the model loads. The request timeout is 75 seconds and CPU inference can exceed it.
- **Unexpected match for an unrelated prompt:** the ranker always returns the nearest three specialties. The evaluation includes these examples to demonstrate this limitation.

See `data/README.md` for provenance and `PROJECT_STATUS.md` for the verification record.

