---
type: "Reference"
title: "Quickstart"
description: "Entry point for the Greek Regional Resilience RAG wiki: the two subsystems, the two API paths, and the minimal steps to run the backend and the Next.js frontend."
tags: ["quickstart", "overview", "routing"]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-01T11:19:44.752Z
sources:
  - id: openwiki-source-6d4b4e707b8d60b6ccfa3425
    resource: repo://.github/workflows/openwiki-update.yml
  - id: openwiki-source-ea70eb6c045047448e446296
    resource: repo://.gitignore
  - id: openwiki-source-eca60e2ced68ba99bd0ac710
    resource: repo://agent.py
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-e3d07093390629e5d2fd7380
    resource: repo://greek_resilient_rag/app/page.tsx
  - id: openwiki-source-ce53fa37ccce38ad987cac49
    resource: repo://greek_resilient_rag/package.json
  - id: openwiki-source-e1d4438011ac1fee7dcab58d
    resource: repo://loader.py
  - id: openwiki-source-833e692518af9eeaf8564cc6
    resource: repo://main.py
  - id: openwiki-source-d37a7a6f6bf2bc7a45be6269
    resource: repo://rag.py
generated: { by: "openwiki/0.4.3", at: "2026-09-01T11:19:44.752Z" }
---

# Quickstart

Greek Regional Resilience RAG answers questions about Greek regional economic and social resilience (2005–2022). The repository is two cooperating subsystems plus a set of offline analysis scripts:

- **Backend** — a Python FastAPI service that loads an Excel workbook into a local ChromaDB index and exposes two endpoints, `POST /ask` and `POST /agent`.
- **Frontend** — a Next.js app (in `greek_resilient_rag/`) that provides a chat UI and posts each question to the backend `POST /agent` endpoint.

The data source of truth is an Excel workbook (`data/stats.xlsx` by default). `loader.py` chunks each workbook sheet into LangChain `Document`s with region/indicator/era metadata, `rag.py` persists those documents into a local `./chroma_db` Chroma store, `main.py` serves the two API paths, and `agent.py` is the LangChain/LangGraph tool agent used by `/agent`.

## Two API paths

- `POST /ask` — fast retrieval-augmented answer. It runs a Chroma similarity search, expands the result set with fuzzy region matching, then asks Gemini (`gemini-2.5-flash`) to answer in the language of the question.
- `POST /agent` — tool-driven research analysis. It delegates the question to the `agent` created in `agent.py` (using `gemini-2.5-pro` and a `MemorySaver` checkpointer) with tools for region search, comparison, resilience scoring, vulnerability indexing, and saving findings.

## Prerequisites

Before running either subsystem, the environment must provide:

- `GEMMA_API_KEY` — Google Gemini API key (required). The backend and agent read it via `os.getenv("GEMMA_API_KEY")`; it is normally placed in a local `.env` file.
- `FILE_PATH` — optional override for the Excel workbook path (defaults to `data/stats.xlsx`).

Two local artifacts are **gitignored and must be supplied or rebuilt locally** — they are not checked into the repository:

- `data/stats.xlsx` — the source workbook (the whole `data/` directory is gitignored).
- `./chroma_db` — the persisted Chroma vector store (gitignored). Rebuild it with `python rag.py` after the workbook is in place.

The frontend additionally depends on the backend running so it can reach `http://localhost:8000/agent`; the backend enables CORS for `http://localhost:3000` specifically.

## Run the backend

1. Create and activate a Python virtual environment, then `pip install -r requirements.txt`.
2. Put a `.env` file containing `GEMMA_API_KEY=your_key` at the repo root, and place your workbook at `data/stats.xlsx`.
3. Build the vector index once: `python rag.py` (loads the six sheets and persists embeddings into `./chroma_db`).
4. Start the server: `uvicorn main:app --reload` (or the Docker equivalent: the `Dockerfile` runs `uvicorn main:app --host 0.0.0.0 --port 8000`).

With the server up, `POST /ask` and `POST /agent` both accept `{"question": "..."}`. The repository also ships a container image build via `Dockerfile` (Python 3.11-slim, exposes port 8000).

## Run the frontend

1. From the `greek_resilient_rag/` directory: `npm install` then `npm run dev` (Next.js dev server on `http://localhost:3000`).
2. The single chat page (`greek_resilient_rag/app/page.tsx`) posts each message to `http://localhost:8000/agent`, so the backend must already be running.
3. For a production build use `npm run build` then `npm run start`; lint with `npm run lint`.

## Task-routing map

This page is the hub. Each domain has a dedicated page — follow these for depth:

- [Architecture overview](architecture/overview.md) — FastAPI backend + Next.js frontend wiring and the data flow from the Excel workbook through `loader.py`/`rag.py` into ChromaDB and through the agent tools.
- [Next.js frontend](architecture/frontend.md) — app-router layout, the single chat page, the `/agent` call, the CORS dependency, and dev/build/lint scripts.
- [Domain concepts](domain/concepts.md) — Greek regions, indicators, eras and crisis periods, resilience scoring (Rs/Rc/D/RTIx), vulnerability index, adaptive-cycle framing, and the `Ελλάδα` national baseline.
- [Workflows](workflows/usage.md) — offline indexing (`rag.py`), `/ask` retrieval with fuzzy region expansion, the `/agent` research protocol (exploratory → diagnostic → synthesis), offline `cluster_analysis.py`, and the frontend interaction loop.
- [Integrations](integrations/external-services.md) — Google Gemini (`gemini-2.5-flash` for `/ask`, `gemini-2.5-pro` for `/agent`), local ChromaDB, pandas/OpenPyXL workbook contract, FastAPI/CORS to the frontend, LangChain/LangGraph, thefuzz, and GitHub Actions.
- [Operations / runbook](operations/runbook.md) — setup and runbook for both subsystems, environment variables, rebuild steps, common failures, and current CI state.
- [Source map](source-map.md) — fast path to tracked source: backend Python modules, the Next.js frontend tree, config/CI files, and change hotspots (excludes gitignored local artifacts).
- [Testing](testing.md) — validation guidance.

## On testing

There are **no tracked tests in the repository now**. The loader test file (`test_loader.py`) is gitignored, and the CI workflow that previously ran `pytest test_loader.py` was removed — the only workflow under `.github/workflows/` is the scheduled OpenWiki update. For how to validate changes manually and the current CI state, see [Testing](testing.md) and [Operations / runbook](operations/runbook.md).

## When changing the repo

- `rag.py` and `loader.py` move together: change the workbook schema or chunking rules in both.
- `agent.py` hard-codes the Excel sheet names and column labels used by the scoring tools, so update it whenever sheet/column names or scoring logic change.
- After any loader or workbook-path change, rebuild `./chroma_db` with `python rag.py`.
- The most fragile parts are the exact Excel sheet names, the hard-coded column labels the scoring tools depend on, and the implicit dependency on a populated local `./chroma_db` directory. If something breaks after a data refresh, inspect `loader.py`, `rag.py`, and the sheet-mapping code in `agent.py` first.
