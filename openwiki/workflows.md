# Workflows

## 1) Build the local vector index

Run `rag.py` when the workbook changes or when `./chroma_db` needs to be rebuilt.

What it does:

1. reads the workbook path from `FILE_PATH` or defaults to `data/stats.xlsx`
2. loads the six expected sheets
3. converts each sheet into `Document` chunks through `loader.py`
4. persists all documents into `./chroma_db`

This is the main offline preparation step for the RAG path.

## 2) Serve the API

Start the FastAPI app from `main.py` with Uvicorn.

Runtime behavior:

- `/ask` performs vector search and prompt-based answer generation
- `/agent` calls the LangChain agent with tool access
- CORS is restricted to `http://localhost:3000`

The app expects the embeddings already to exist locally.

## 3) Run the research agent

The agent path in `agent.py` is intended for questions that require calculations or comparisons. The tools are organized around the workbook schema, not around general-purpose internet research.

Typical cases:

- compare two regions on the same indicator and era
- compute percent change between years
- classify resilience behavior
- summarize the coupling between economic and social trends

A notable implementation detail is that `main.py` passes a fixed `thread_id` into the agent config. That may matter if the app is used concurrently.

## 4) Produce deeper narrative synthesis

`deepresearch.py` is a separate script for literature-style synthesis. It reads the long DOCX file in the repository, uses Gemini with search-style tooling, and writes the result to `literature_synthesis.md`.

This is best treated as a generated research artifact rather than part of the API runtime.

## 5) Explore region structure

`cluster_analysis.py` is an exploratory analysis workflow. It produces plots such as `cluster_scatter.png` and `cluster_radar.png` from derived region features.

This looks more like an offline analysis notebook translated into a script than a serving path.

## 6) Validate the loader

`test_loader.py` exercises the workbook loader directly.

Key checks:

- every configured sheet returns some documents
- the first sheet produces the expected chunk count
- document metadata includes `region`, `indicator`, `era`, and `source`
- invalid paths raise `FileNotFoundError`

## 7) CI behavior

`.github/workflows/tests.yml` runs the loader test suite on pushes to `main` using Python 3.11.

The tests are data-dependent, so the suite skips some checks in CI when the Excel file is not present.

## Source references

- `rag.py`
- `main.py`
- `agent.py`
- `deepresearch.py`
- `cluster_analysis.py`
- `test_loader.py`
- `.github/workflows/tests.yml`
