---
type: "Reference"
title: "Testing"
description: "Current validation status for the Greek Regional Resilience RAG: there are no tracked tests, CI runs only the OpenWiki documentation refresh, and the only validation is manual checks against rag.py ingestion and the /ask and /agent endpoints."
tags: ["testing", "ci", "validation", "rag", "fastapi", "agent"]
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
  - id: openwiki-source-833e692518af9eeaf8564cc6
    resource: repo://main.py
  - id: openwiki-source-d37a7a6f6bf2bc7a45be6269
    resource: repo://rag.py
generated: { by: "openwiki/0.4.3", at: "2026-09-01T11:19:44.752Z" }
---

# Testing

## Current test coverage

There are **no tracked tests** in the repository. The project previously had a `test_loader.py` pytest module, but it is no longer version-controlled:

- `.gitignore` lists `test_loader.py`, so a fresh clone does not contain it and it is a local-only artifact.
- `.github/workflows/tests.yml`, which previously ran `pytest test_loader.py`, has been deleted from `.github/workflows/`.

Because the test file is gitignored and the workflow is gone, `pytest` does not run anywhere in CI. Do not assume the repository has a passing test suite; validation is manual.

## CI

The only committed GitHub Actions workflow is `.github/workflows/openwiki-update.yml`, the OpenWiki documentation refresh. It does not run the application or any tests. It triggers on a monthly schedule (`cron: '0 6 1 * *'`) and on `workflow_dispatch`, installs the `openwiki` CLI globally, runs `openwiki code --update --print` with the OpenRouter provider (model `z-ai/glm-5.2`), and opens a `docs: update OpenWiki` pull request via `peter-evans/create-pull-request` scoped to `openwiki`, `AGENTS.md`, `CLAUDE.md`, and the workflow itself.

In short: CI only refreshes documentation; it provides no application-level validation.

## Manual validation steps

With no automated tests, the following manual checks are the actual validation procedure. They all assume the workbook is present at `FILE_PATH` (default `data/stats.xlsx`) and that `GEMMA_API_KEY` is set in `.env`, because `rag.py`, `main.py`, and `agent.py` all fail without them.

### After loader or workbook changes

1. Rebuild the vector index: `python rag.py`.
2. Confirm the script reports a non-zero chunk count for **all six** sheets: `Normal Οικον Βάση`, `Normal Οικον Βάση - Crisis`, `Normal Οικον Βάση - COVID`, `Normal Κοινων Βάση`, `Normal Κοινων Βάση - Crisis`, `Normal Κοινων Βάση - COVID`.
3. Manually verify that `loader.py` produces non-empty documents for each sheet — `rag.py` prints `Loaded {len(docs)} chunks from {sheet}` per sheet and `Done! Stored {len(all_docs)} chunks.` at the end.

A sheet reporting zero chunks, or a `KeyError`/`FileNotFoundError` during ingestion, means the loader or workbook schema drifted and must be fixed before restarting the backend.

### After API or agent changes

There are no endpoint tests for the FastAPI routes, so exercise the backend by hand after regenerating the Chroma store:

1. Rebuild the index with `python rag.py` if the workbook changed.
2. Start the API: `uvicorn main:app --reload` (port 8000 by convention).
3. Manually exercise `POST /ask` with a short, factual, region-grounded question and confirm it returns `{"answer": ...}`.
4. Manually exercise `POST /agent` with a question that requires a calculation or comparison (e.g. a resilience score or two-region comparison) and confirm the agent invokes its workbook-reading tools and returns a text `answer`.

Optionally, if `test_loader.py` happens to exist on your machine (it is gitignored, so this is not guaranteed), `pytest test_loader.py` can be run locally for loader-level checks. It is not part of CI and is absent in a clean clone.

## Risks to watch

- **No tracked tests / no CI tests.** `test_loader.py` is gitignored and `tests.yml` is gone, so nothing validates the loader, endpoints, or agent automatically. Regressions surface only when someone runs the manual checks above.
- **Schema drift breaks tools.** The calculation tools in `agent.py` assume exact column labels (e.g. `Resistance (2008-2013)`, `Recovery (2013-2019)`, `% National Change 2013-2019`) and exact sheet names. A workbook column rename raises a `KeyError` or produces a fuzzy mismatch; a sheet rename breaks both `rag.py` indexing and the tool reads. There is no test to catch this — verify `loader.py`, `rag.py`, and the `agent.py` tools together after any schema change.
- **No endpoint tests.** There is no automated coverage of `POST /ask` or `POST /agent`, including their retrieval/fuzzy-matching logic (`main.py`), the LangGraph agent delegation, and the list-shaped-answer normalization in `/agent`. Changes to request/response behavior must be validated by the manual endpoint checks above.
- **Index freshness is unverified.** `./chroma_db` is a build-time artifact rebuilt by `python rag.py`. If it is missing or stale relative to the workbook, `/ask` retrieval and the `search_regions`/`compare_regions` tools silently return outdated or empty results; no test enforces a rebuild.

## If tests are reintroduced

If `test_loader.py` (or any other test module) is brought back under version control and/or a test workflow is restored to `.github/workflows/`, update this page **and** `/openwiki/source-map.md` together so the test file, the CI workflow, and the validation procedure stay consistent.

## Related pages

- [/openwiki/operations/runbook.md](/openwiki/operations/runbook.md) — local setup, environment variables, rebuild steps, common failures, and the CI description.
- [/openwiki/source-map.md](/openwiki/source-map.md) — tracked source files, change hotspots, and the generated/local artifact list (which includes `test_loader.py`).
- [/openwiki/workflows/usage.md](/openwiki/workflows/usage.md) — the `/ask` and `/agent` request flows this page asks you to exercise manually.
