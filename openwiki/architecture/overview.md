# Architecture overview

## System shape
This project is a single-process FastAPI application backed by a local ChromaDB vector store and an Excel workbook.
It has two user-facing API paths:
- `POST /ask` for retrieval-augmented answers from the indexed workbook chunks.
- `POST /agent` for longer, tool-driven analysis via LangChain/LangGraph.

## Main components
- **`main.py`** wires FastAPI, CORS, the Gemini chat model, the Chroma retriever, and the agent endpoint.
- **`loader.py`** converts spreadsheet rows into `langchain_core.documents.Document` objects with region/indicator/era metadata.
- **`rag.py`** loads all configured sheets from the workbook and persists them to `./chroma_db`.
- **`agent.py`** defines the research tools that read from the workbook directly and perform fuzzy matching, comparison, and derived metric calculations.
- **`cluster_analysis.py`** is an offline analysis/plotting script that derives the cluster visualizations shipped with the repository.

## Data flow
1. `rag.py` reads workbook sheets from `FILE_PATH` or `data/stats.xlsx`.
2. `loader.py` normalizes headers, skips the national row, and emits per-region documents.
3. `Chroma.from_documents(...)` persists embeddings to `./chroma_db`.
4. `main.py` loads `Chroma(persist_directory="./chroma_db")` at startup.
5. `/ask` performs similarity search, then enriches the result set if fuzzy region matching finds additional relevant regions.
6. `/agent` invokes the LangChain agent, which calls direct workbook-backed tools rather than the vector store.

## Retrieval vs. tool use
The repo deliberately supports two styles of question answering:
- **RAG path:** good for quick answers grounded in semantically similar workbook chunks.
- **Agent path:** good for calculations, comparisons, and region-specific diagnostics where direct spreadsheet access is more reliable.

## Design implications
- The vector store is local and expected to be rebuilt from the workbook, not treated as a remote source of truth.
- Many behaviors assume the workbook contains Greek region names and the exact sheet labels referenced in `agent.py` and `rag.py`.
- The app relies on fuzzy matching to soften user input, but the underlying data model remains strict about sheet and column naming.

## Source anchors
- `main.py`
- `agent.py`
- `loader.py`
- `rag.py`
- `cluster_analysis.py`
