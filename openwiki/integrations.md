# Integrations

## Gemini

The application uses Google Gemini through LangChain in two places:

- `main.py` uses `ChatGoogleGenerativeAI(model="gemini-2.5-flash")` for quick RAG answers
- `agent.py` uses `ChatGoogleGenerativeAI(model="gemini-2.5-pro")` for the tool-using research agent

The code reads the API key from the environment variable `GEMMA_API_KEY`.

## ChromaDB

Chroma is the local retrieval layer.

- `rag.py` writes the persisted store to `./chroma_db`
- `main.py` and `agent.py` both open that same persisted directory at runtime

The vector store is treated as a local artifact, not an external service.

## pandas / OpenPyXL

The workbook logic relies on pandas reading Excel sheets. `loader.py` and most tools in `agent.py` use `pd.read_excel(...)` and then normalize column names.

This means workbook shape and column names are part of the integration contract.

## FastAPI / CORS

`main.py` exposes a FastAPI app and adds CORS middleware for `http://localhost:3000`.

That suggests an external frontend or local UI is expected during development, even though the frontend is not documented in the current source set.

## LangChain / LangGraph

`agent.py` uses LangChain tools and `MemorySaver` from LangGraph checkpointing.

The repo uses LangChain in two modes:

- retrieval and string-prompt composition for `/ask`
- tool-based agent orchestration for `/agent`

## Fuzzy matching

The code uses `thefuzz` / RapidFuzz-style matching to:

- detect region names in user questions
- map approximate region inputs to workbook rows
- normalize user-entered indicator names

This is a small but important usability layer.

## GitHub Actions

Two workflows exist under `.github/workflows/`:

- `tests.yml` runs pytest on pushes to `main`
- `openwiki-update.yml` refreshes the generated OpenWiki docs

## Source references

- `main.py`
- `agent.py`
- `loader.py`
- `rag.py`
- `.github/workflows/tests.yml`
- `.github/workflows/openwiki-update.yml`
