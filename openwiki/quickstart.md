# Quickstart

Greek Regional Resilience RAG is a FastAPI service for querying and analyzing Greek regional economic and social resilience indicators. The repository centers on two API paths:

- `POST /ask` for fast retrieval-augmented answers from a local ChromaDB index
- `POST /agent` for tool-driven analysis over the same Excel-backed data

The source of truth is an Excel workbook under `data/stats.xlsx` by default. `rag.py` turns workbook sheets into Chroma documents, `main.py` serves retrieval queries, and `agent.py` adds calculation and comparison tools for deeper analysis.

## Start here

- [Architecture overview](architecture/overview.md) — how the app is wired together
- [Domain concepts](domain/concepts.md) — regions, indicators, eras, crisis periods, and scoring logic
- [Workflows](workflows/usage.md) — indexing, serving, research synthesis, and exploratory analysis
- [Operations runbook](operations/runbook.md) — setup, environment variables, and rebuild steps
- [Testing](testing.md) — what is covered, what is skipped in CI, and how to validate changes
- [Source map](source-map.md) — fast path back to the code

## What this repo contains

Core runtime files:

- `main.py` — FastAPI entrypoint with `/ask` and `/agent`
- `agent.py` — LangChain/LangGraph tool agent and analysis helpers
- `loader.py` — Excel-to-document chunking for vector search
- `rag.py` — offline indexing script that persists embeddings into `./chroma_db`
- `test_loader.py` — loader tests

Supporting evidence and artifacts:

- `README.md` — brief setup and endpoint summary
- `.github/workflows/tests.yml` — CI for `pytest test_loader.py`
- `cluster_analysis.py` — exploratory clustering analysis with saved plots
- `deepresearch.py` — literature synthesis script using Gemini and search tools
- `findings.md` / `literature_synthesis.md` — generated research notes

## Repository shape

The app is intentionally small but opinionated:

- data is loaded from Excel rather than a database
- ChromaDB is used as the local retrieval layer
- Gemini powers both direct answers and the research agent
- fuzzy region matching makes natural-language inputs more forgiving
- most business rules live in `agent.py`, not in a separate service layer

## Important setup assumptions

The code expects:

- `GEMMA_API_KEY` in the environment for Gemini access
- `FILE_PATH` optionally set to override the Excel workbook path
- a readable workbook at `data/stats.xlsx` by default
- a populated local Chroma store in `./chroma_db` for serving queries

## When changing the repo

- Update `rag.py` and `loader.py` together when the workbook schema or chunking rules change.
- Update `agent.py` whenever sheet names, column names, or scoring logic change.
- Re-run `test_loader.py` after any loader or workbook-path change.
- Review the CI workflow if tests become data-dependent or expand beyond the loader.

## Notes for future agents

The most fragile parts of the repository are the exact Excel sheet names, the hard-coded column labels used by the scoring tools, and the implicit dependency on a local `chroma_db` directory. If something breaks after a data refresh, inspect `loader.py`, `rag.py`, and the sheet mapping code in `agent.py` first.
