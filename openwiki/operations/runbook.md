# Operations / runbook

## Local setup
The README gives the canonical local flow:
1. Create a virtual environment.
2. Install `requirements.txt`.
3. Provide an `.env` with `GEMMA_API_KEY`.
4. Place the workbook at `data/stats.xlsx` or point `FILE_PATH` elsewhere.
5. Run `python rag.py` to build `./chroma_db`.
6. Start the API with `uvicorn main:app --reload`.

## Environment variables
- `GEMMA_API_KEY` — used by `main.py`, `agent.py`, and `deepresearch.py` for Gemini access.
- `FILE_PATH` — workbook location override used by `loader.py`, `rag.py`, and `agent.py`.
- `CI` — used by `test_loader.py` to skip workbook-dependent tests in CI.

## Common operational concerns
### Missing workbook
If the spreadsheet is absent, loader and agent functions that call `pandas.read_excel(...)` will fail.
The current tests explicitly skip in CI when that file is unavailable.

### Missing or stale ChromaDB index
If `/ask` returns poor results or startup fails around ChromaDB, rebuild the index with `python rag.py`.
The app expects a local `./chroma_db` directory.

### Sheet and column drift
Most tool functions assume fixed sheet names and expected columns.
If the workbook changes, verify the loader, vector build, and all workbook-backed tools together.

### Fuzzy matching surprises
The system uses fuzzy matching to map user phrasing to regions and indicators.
That is helpful for usability, but it can also silently choose the wrong region if workbook labels drift.

## Git/CI notes
- The recent history shows repeated fixes for file paths to rely on environment variables rather than hard-coded paths.
- CI now skips data-dependent tests when the workbook is unavailable, which is important for repository portability.
- A dedicated OpenWiki GitHub Action exists at `.github/workflows/openwiki-update.yml` to refresh the documentation automatically.

## Helpful checks
- `pytest test_loader.py`
- rebuild the index after workbook or sheet changes
- sanity-check `/ask` and `/agent` after changing the data schema or tools
