# Architecture overview

The repository is a compact RAG-style FastAPI application with a second, tool-using research path.

## Request paths

### `POST /ask`
Defined in `main.py`, this path:

1. receives a `question`
2. searches the local Chroma collection with `similarity_search(..., k=10)`
3. expands retrieval with fuzzy region matching for common Greek region names
4. concatenates the matching document text into prompt context
5. sends the prompt to Gemini and returns a short answer

This path is optimized for quick, context-grounded answers rather than multi-step reasoning.

### `POST /agent`
Also defined in `main.py`, this path delegates to the LangChain/LangGraph agent from `agent.py`. The agent is built around Gemini 2.5 Pro and a set of tool functions that can:

- retrieve region/indicator/era slices from Chroma
- compare two regions
- calculate percent change from Excel values
- calculate resilience scores and RTI-style scores
- analyze recovery speed, socio-economic coupling, and structural shift

This is the path for more analytical questions that need calculations rather than just retrieval.

## Data flow

The project uses a simple offline indexing pipeline:

1. `loader.py` reads a workbook sheet into rows of regional data
2. `rag.py` iterates the six expected sheets and converts them into LangChain `Document` objects
3. `rag.py` writes those documents into `./chroma_db`
4. `main.py` loads the persisted Chroma store at startup
5. queries hit the store directly through similarity search or filtered search

## Core components

### `main.py`
- loads environment variables with `python-dotenv`
- initializes `ChatGoogleGenerativeAI(model="gemini-2.5-flash")`
- sets up CORS for `http://localhost:3000`
- exposes the FastAPI app

### `agent.py`
- constructs the tool library
- reads the workbook path from `FILE_PATH` or defaults to `data/stats.xlsx`
- uses Chroma for metadata-filtered retrieval
- uses pandas and fuzzy matching for workbook-based calculations
- keeps conversational memory via `MemorySaver`

### `loader.py`
- normalizes workbook headers
- groups columns into indicators and eras
- emits `Document` chunks with metadata for `region`, `indicator`, `era`, and `source`

### `rag.py`
- loads all expected workbook sheets
- persists embeddings into `./chroma_db`
- prints per-sheet and total chunk counts during indexing

## Design constraints

The architecture assumes:

- a local workbook with exact sheet names
- stable column naming conventions in the workbook
- a writable local Chroma directory
- a Gemini API key available at runtime

The code favors direct, readable data logic over abstraction. That makes it easy to inspect but also means schema drift can break requests quickly.

## Source references

- `main.py`
- `agent.py`
- `loader.py`
- `rag.py`
- `README.md`
