# launch-docs-rag-pipeline (local, zero-cost)

A local pipeline that turns **release notes → LLM-ready docs + JSON**, builds a **searchable index**, answers **support Q&A with citations & youth-safety guardrails**, and runs **basic evaluations**.

- runs 100% locally with **Ollama + Mistral** and **FAISS**
- no auth keys, no cloud costs
- meant as a “day-one” AI-enablement starter

---

## Features

- **01_refine_docs** → Raw notes →  
  - `artifacts/doc.md` (clean, human-readable brief)  
  - `artifacts/doc.json` (structured “prompt-pack inputs”: overview, key changes, steps, FAQs, safety notes, etc.)
- **02_build_index** → Chunks + embeds docs and stores them in a **FAISS** vector index (local, fast).
- **03_query** → RAG-style Q&A with citations and youth-safety defaults.
- **04_eval** → Lightweight checks for sourcing and safe language.

---

## Tech stack (why)

- **Ollama** – local model runtime with a simple API, zero cost.
- **Mistral** – small + fast model that’s great for structured outputs on CPU.
- **LangChain (0.3.x)** – prompt templating & text splitting (no special Ollama integration needed).
- **Sentence-Transformers (all-MiniLM-L6-v2)** – free, strong embeddings.
- **FAISS** – *Fa*cebook *AI* *S*imilarity *S*earch; blazing-fast local vector search.

---

## Repo layout

```
launch-docs-rag-pipeline/
├─ data/
│  ├─ release_notes.md         # your raw notes (edit me)
│  ├─ policy.md                # optional policy/safety snippets (edit me)
│  └─ previous_article.md      # optional previous doc for diffs
├─ artifacts/                  # generated outputs (created by scripts)
│  ├─ doc.md
│  ├─ doc.json
│  └─ eval_results.json
├─ index/
│  └─ faiss.index              # vector store (created by step 2)
├─ 01_refine_docs.py
├─ 02_build_index.py
├─ 03_query.py
├─ 04_eval.py
├─ requirements.txt
├─ Makefile
└─ README.md
```

---

## Prerequisites

- macOS/Linux with **Python 3.12**
- **Ollama** app installed & running (download: https://ollama.com)
- Models (pull in a terminal):
  ```bash
  ollama pull mistral
  # optional/heavier:
  # ollama pull llama3.1
  ```

---

## Setup (first time)

```bash
# clone or cd into your project folder
cd path/to/launch-docs-rag-pipeline

# create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install deps
pip install --upgrade pip
pip install -r requirements.txt

# sanity check: make sure ollama model responds
ollama run mistral "hello"
```

---

## Usage

### 1) Refine docs (release notes → Markdown + JSON)

Put your raw notes in `data/release_notes.md`  
(optional) edit `data/policy.md` and `data/previous_article.md`

Run:
```bash
python 01_refine_docs.py
```

Outputs:
- `artifacts/doc.md` (human-readable)
- `artifacts/doc.json` (machine-readable)

If parsing fails, the script prints a truncated raw model output so you can see what happened.

---

### 2) Build index (make it searchable with FAISS)

```bash
python 02_build_index.py
```

What happens:
- loads `artifacts/doc.json`
- collects text fields (overview, changes, FAQs, etc.)
- **embeds** chunks with `sentence-transformers/all-MiniLM-L6-v2`
- builds a local **FAISS** index → `index/faiss.index`
- writes `artifacts/corpus.txt` (a simple human-readable copy)

> **FAISS in plain English:** we convert each text chunk into a numeric vector (an “embedding”), then store all vectors in FAISS. Later, we also embed your question and ask FAISS, “which stored vectors are most similar?” That’s your fast, local semantic search.

---

### 3) Q&A with safety & citations

```bash
python 03_query.py
```

You’ll get:
```
Ask a question (or 'quit'):
```

Try:
- `What changed in this release?`
- `Who can start breakout rooms?`
- `List any known limitations.`

Flow:
- your question is embedded → FAISS returns top-k relevant chunks
- question + snippets go to Mistral
- the assistant answers concisely, cites sources (e.g., `[1]`, `[2]`), and avoids unsafe guidance

---

### 4) Evaluate (light checks)

```bash
python 04_eval.py
```

Outputs:
- `artifacts/eval_results.json` — simple automated checks:
  - `has_citation` → did the answer include a citation?
  - `mentions_todo` → did it leak “TODO”s (missing info)?
  - `safe_language` → crude banned-phrase screen (e.g., PII terms)

You can expand this into proper RAGAS metrics later if you want.

---

## Switching models (optional)

Change `model="mistral"` to any pulled Ollama model:
```python
ollama.chat(model="llama3.1", messages=..., options={"temperature": 0.2})
```
Heavier models may be slower on CPU; `mistral` is a great default.

---

## Troubleshooting

- **Script “hangs”** → Ollama is probably still loading the model. Test:
  ```bash
  ollama run mistral "hello"
  ```
  If that returns quickly, re-run your script.

- **`ModuleNotFoundError: ollama`** → install the Python client **inside the venv**:
  ```bash
  source .venv/bin/activate
  pip install ollama
  ```

- **NumPy / torch mismatch** → ensure you’re inside the venv and using the pinned `requirements.txt` (with `numpy<2`, `torch==2.2.2` for mac).

- **`python3` runs system Python** → your shell may alias it. Use the venv binary:
  ```bash
  .venv/bin/python 01_refine_docs.py
  ```
  or verify:
  ```bash
  which python
  # should be .../.venv/bin/python
  ```

---

## Performance tips

- Keep `options={"temperature": 0.2}` for predictable formatting.
- Add `num_predict` in Ollama options to cap long replies.
- Prefer `mistral` on CPU laptops; switch to larger models if you need more reasoning quality.

---

## How to extend

- **Prompt packs**: turn slices of `doc.json` into a single system prompt file for agents.
- **True eval**: add RAGAS or custom checks (faithfulness, answer relevancy).
- **Automation**: run 01→04 on every commit to `data/release_notes.md` (GitHub Action / Makefile).
- **More knowledge**: drop additional product docs in `data/` and re-run 01→02 to refresh the index.

---

## Quick commands (cheat sheet)

```bash
# once
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ollama pull mistral

# every update
python 01_refine_docs.py
python 02_build_index.py
python 03_query.py
python 04_eval.py
```

---

## .gitignore (recommended)

```gitignore
# venvs
.venv/
venv/

# macOS cruft
.DS_Store

# python cache
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.ipynb_checkpoints/
.pytest_cache/

# local env / secrets
.env
*.env

# logs
*.log

# build artifacts (generated)
artifacts/doc.md
artifacts/doc.json
artifacts/eval_results.json

# vector index (binary, machine-specific)
index/
```

---

## Makefile (optional but handy)

```makefile
VENV=.venv
PY=$(VENV)/bin/python

init:
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

refine:
	$(PY) 01_refine_docs.py

index:
	$(PY) 02_build_index.py

ask:
	$(PY) 03_query.py

eval:
	$(PY) 04_eval.py
```
