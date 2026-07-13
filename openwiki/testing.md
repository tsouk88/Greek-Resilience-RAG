# Testing

## Current coverage

The only explicit test module in the repository is `test_loader.py`.

It checks:

- each configured sheet can be loaded into documents
- the loader returns the expected number of chunks for the baseline sheet
- generated documents include the expected metadata keys
- an invalid workbook path raises `FileNotFoundError`

## CI

`.github/workflows/tests.yml` installs dependencies and runs:

```bash
pytest test_loader.py
```

The tests are skipped in CI when `CI=true` and the Excel file is unavailable, so the pipeline mainly verifies test wiring unless the workbook is present in the runner environment.

## How to validate changes locally

If you modify the workbook loader, sheet names, or column normalization:

1. rebuild embeddings if needed with `python rag.py`
2. run `pytest test_loader.py`
3. manually verify that `loader.py` still produces non-empty documents for all six sheets

If you modify the API or agent logic, there are no dedicated tests yet. Use manual checks against the `/ask` and `/agent` endpoints after regenerating the Chroma store.

## Risks to watch

- test expectations are tightly coupled to the current workbook schema
- the suite depends on a local Excel file path, so environment setup matters
- there are no endpoint tests for FastAPI routes yet
- calculation tools in `agent.py` assume exact column labels and can fail with schema drift

## Source references

- `test_loader.py`
- `.github/workflows/tests.yml`
- `loader.py`
- `rag.py`
