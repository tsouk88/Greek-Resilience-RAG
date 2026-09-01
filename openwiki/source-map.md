---
type: "Reference"
title: "Source map"
description: "Fast path to the tracked source files behind the Greek Regional Resilience RAG: backend Python modules, the Next.js frontend tree, and the config/CI files. Notes which paths are generated/local artifacts and where each kind of change should start."
tags: [source-map, backend, frontend, rag, langchain, fastapi, nextjs, ci]
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
  - id: openwiki-source-a8c63260b711c81dc8d31ae6
    resource: repo://cluster_analysis.py
  - id: openwiki-source-bb1ebe868e35e9e500714501
    resource: repo://Dockerfile
  - id: openwiki-source-ffff44069204183852ba2640
    resource: repo://greek_resilient_rag/app/globals.css
  - id: openwiki-source-ae8c686ae1cc5911a4b5c0c1
    resource: repo://greek_resilient_rag/app/layout.tsx
  - id: openwiki-source-e3d07093390629e5d2fd7380
    resource: repo://greek_resilient_rag/app/page.tsx
  - id: openwiki-source-8161ebd42a7b9aa30d983941
    resource: repo://greek_resilient_rag/eslint.config.mjs
  - id: openwiki-source-348ca66d9b517d55c257238c
    resource: repo://greek_resilient_rag/next.config.ts
  - id: openwiki-source-ce53fa37ccce38ad987cac49
    resource: repo://greek_resilient_rag/package.json
  - id: openwiki-source-ab75648576dd6302c5f4e241
    resource: repo://greek_resilient_rag/postcss.config.mjs
  - id: openwiki-source-b6722038ca26d9f76a28f05e
    resource: repo://greek_resilient_rag/tsconfig.json
  - id: openwiki-source-e1d4438011ac1fee7dcab58d
    resource: repo://loader.py
  - id: openwiki-source-833e692518af9eeaf8564cc6
    resource: repo://main.py
  - id: openwiki-source-d37a7a6f6bf2bc7a45be6269
    resource: repo://rag.py
  - id: openwiki-source-373640cd8a0886cee69db282
    resource: repo://requirements.txt
generated: { by: "openwiki/0.4.3", at: "2026-09-01T11:19:44.752Z" }
---

# Source map

This map covers only **tracked** repository files. Several analysis-related paths exist on disk but are gitignored generated/local artifacts (see [Generated and local artifacts](#generated-and-local-artifacts)) and are not treated as source.

## Backend entry points

- `main.py` — the FastAPI application and its two HTTP endpoints. It constructs the Gemini LLM (`gemini-2.5-flash`), opens the shared `./chroma_db` Chroma vectorstore, and registers CORS for `http://localhost:3000` so the Next.js UI can call it.
  - `POST /ask` — retrieval-augmented chat: runs `vectorstore.similarity_search` (k=10), then fuzz-matches Greek region names in the question with `thefuzz` and, for any matched region not already present, runs an additional filtered search (`filter={"region": region}`) to guarantee regional coverage. The merged context is sent to the Gemini chain with a fixed analyst prompt and returned as `{"answer": ...}`.
  - `POST /agent` — delegates to the LangGraph agent built in `agent.py` via `agent.invoke(...)` with a fixed `thread_id` (`"research-session-3"`) for memory continuity, and normalizes list-shaped answers back to text.
- `rag.py` — offline ingestion script. Reads the six workbook sheets listed below through `loader.load_excel_data`, concatenates the resulting `Document` lists, and builds the persistent Chroma store with `Chroma.from_documents(..., persist_directory="./chroma_db")`. Run once (or whenever the workbook changes) to populate the vectorstore that `main.py` and `agent.py` query.
- `agent.py` — the analytical agent. Builds a `create_agent` (LangChain/LangGraph) over `gemini-2.5-pro` with a `MemorySaver` checkpointer and a long `system_prompt` that orchestrates an Exploratory → Diagnostic → Synthesis research protocol. It exports the `agent` object imported by `main.py`.

### Sheets consumed by `rag.py`
`Normal Οικον Βάση`, `Normal Οικον Βάση - Crisis`, `Normal Οικον Βάση - COVID`, `Normal Κοινων Βάση`, `Normal Κοινων Βάση - Crisis`, `Normal Κοινων Βάση - COVID`.

## Data shaping

- `loader.py` — `load_excel_data(file_path, sheet_label)` converts a workbook sheet into LangChain `Document` chunks. For each non-national region (`Ελλάδα` row is used as the national reference and skipped from output) it groups years into three eras — `Expansion (Προ Κρίσης)`, `Crisis (Κρίση)`, `Recovery (Ανάκαμψη)` — and emits one document per (region, indicator, era) with metadata `region`, `indicator`, `era`, and `source` (the sheet label). This metadata is what `agent.py`'s `search_regions` filters on and what `main.py`'s region-aware retrieval relies on.

## Analytical scoring and classification

- `agent.py` — exposes the scoring/classification tools the agent calls during its protocol. Each tool reads the workbook at `os.getenv("FILE_PATH", "data/stats.xlsx")`, fuzzy-matches the requested region name against the sheet's region column with `thefuzz.process.extractOne` (threshold score > 70), and returns a numeric result plus a label:
  - `calculate_resilience_score` — resistance + recovery vs. national, classifies **Transformative / Adaptive / Vulnerable**.
  - `calculate_rti_score` — Trajectory Divergence (Rs, Rc, D) vs. regional medians, classifies **Transformative / Adaptive / Emerging Transformative / Vulnerable**.
  - `calculate_rtix_score` — composite `RTIx = 0.50·D + 0.30·Rc + 0.20·Rs`, vulnerability-adjusted, classifies **Strongly/Moderately Transformative / Stagnant / Declining Trajectory**.
  - `calculate_recovery_speed`, `analyze_socioeconomic_coupling`, `calculate_structural_shift`, `calculate_crisis_comparison`, `calculate_vulnerability_index`, `calculate_percent_change` — supporting diagnostics.
  - `search_regions` / `compare_regions` — Chroma queries filtered by `region`/`indicator`/`era` metadata (the `era` argument is normalized through an `era_map`).
  - `save_finding` / `read_findings` — append/read the local `findings.md` notebook (see [Generated and local artifacts](#generated-and-local-artifacts)).
- `cluster_analysis.py` — a standalone KMeans clustering script. It embeds a hardcoded RTIx-derived dataset for the 13 Greek regions (averaging economic and social Rs/Rc/D), standardizes features, selects `k` via silhouette score (hard-set to 4), names clusters in Greek, and renders two figures: `cluster_scatter.png` and `cluster_radar.png`. **The script is tracked; its PNG outputs are gitignored.**

## Frontend tree (`greek_resilient_rag/`)

A Next.js 16 / React 19 app (Tailwind CSS v4 via PostCSS) that provides the chat UI for the agent.

- `greek_resilient_rag/app/page.tsx` — the client component and sole screen. Maintains a `Message[]` state, posts each user input to `http://localhost:8000/agent` (the backend `/agent` endpoint), and renders the conversation with Greek labels ("Εσύ" / "Agent", "Αποστολή", "Σκέφτομαι…"). This is the primary frontend change hotspot.
- `greek_resilient_rag/app/layout.tsx` — root layout, Geist fonts, and default metadata.
- `greek_resilient_rag/app/globals.css` — Tailwind import plus theme/color variables.
- `greek_resilient_rag/package.json` — scripts (`dev`, `build`, `start`, `lint`) and dependencies (Next 16.2.6, React 19.2.4, Tailwind v4, TypeScript, ESLint).
- `greek_resilient_rag/next.config.ts` — minimal Next config (currently empty options).
- `greek_resilient_rag/tsconfig.json` — TypeScript paths (`@/*` → `./*`) and Next plugin.
- `greek_resilient_rag/eslint.config.mjs` — flat ESLint config using `eslint-config-next` core-web-vitals + TypeScript.
- `greek_resilient_rag/postcss.config.mjs` — registers `@tailwindcss/postcss`.

## Config and CI

- `requirements.txt` — pinned Python dependency set, including FastAPI, Uvicorn, LangChain (`langchain`, `langchain-chroma`, `langchain-google-genai`, `langgraph` + checkpointer/prebuilt), ChromaDB, pandas, NumPy, scikit-learn, matplotlib, `adjustText`, `thefuzz`/`RapidFuzz`, and pytest. (`requirements.txt` is UTF-16 encoded in the repo.)
- `Dockerfile` — `python:3.11-slim` image that installs `requirements.txt`, copies the app, exposes 8000, and runs `uvicorn main:app`.
- `.github/workflows/openwiki-update.yml` — the only tracked CI workflow. Scheduled monthly (`cron: '0 6 1 * *'`, plus `workflow_dispatch`) to run `openwiki code --update --print` and open a `docs: update OpenWiki` pull request scoped to `openwiki`, `AGENTS.md`, `CLAUDE.md`, and the workflow itself.

## Change hotspots

When modifying behavior, start with the following code paths:

- Workbook schema or location changes → `loader.py` (chunking/metadata), `rag.py` (sheet list and ingestion), `agent.py` (sheet names and column references inside scoring tools), and loader test validation (the `test_loader.py` test is a gitignored local artifact — see below).
- Request/response behavior → `main.py` (endpoint handlers, retrieval logic, prompt, CORS).
- Analytical scoring or region classification → `agent.py` (tool functions and the `system_prompt`) and `cluster_analysis.py` (cluster naming/figures).
- Frontend UI → `greek_resilient_rag/app/page.tsx`.
- CI/documentation refresh → `.github/workflows/openwiki-update.yml`.

## Generated and local artifacts

The following paths exist locally but are **gitignored** (per `.gitignore`) and are *not* tracked source; do not cite them as source and do not rely on them being present in a clean checkout:

- `chroma_db/` — the persisted Chroma vectorstore produced by `rag.py`.
- `data/` (including `data/stats.xlsx`) — the input workbook read by `loader.py`, `rag.py`, and the `agent.py` tools via `FILE_PATH`.
- `findings.md` — the append-only findings notebook written by `agent.py`'s `save_finding` tool and read by `read_findings`.
- `literature_synthesis.md` — generated literature review.
- `deepresearch.py` — local Gemini-driven synthesis generator.
- `test_loader.py` — local loader test/validation.
- `cluster_scatter.png`, `cluster_radar.png` — figures emitted by the tracked `cluster_analysis.py`.
- `venv/`, `.venv/`, `.env`, `__pycache__/`, `*.docx`.

## Notes for future agents

- The repository contains generated analysis artifacts that are evidence of the project's intended interpretation, not tracked source. Treat `findings.md` and `cluster_analysis.py`'s embedded dataset as framing material; prefer the current source code and recent git history for implementation details.
- If code and narrative disagree, prefer the current source code for implementation details, and use the generated narratives (when present locally) to understand the intended framing.
