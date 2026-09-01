---
type: "Reference"
title: "External service integrations"
description: "The libraries and services the backend integrates with: Google Gemini (flash + pro), local ChromaDB, pandas/OpenPyXL workbook contract, FastAPI/CORS to the Next.js frontend, LangChain/LangGraph agent, thefuzz matching, and the OpenWiki GitHub Action."
tags: ["integrations", "gemini", "chromadb", "pandas", "openpyxl", "fastapi", "cors", "langchain", "langgraph", "thefuzz", "github-actions"]
verified:
  - by: openwiki/0.4.3
    at: 2026-09-01T11:19:44.752Z
sources:
  - id: openwiki-source-6d4b4e707b8d60b6ccfa3425
    resource: repo://.github/workflows/openwiki-update.yml
  - id: openwiki-source-eca60e2ced68ba99bd0ac710
    resource: repo://agent.py
  - id: openwiki-source-e3d07093390629e5d2fd7380
    resource: repo://greek_resilient_rag/app/page.tsx
  - id: openwiki-source-e1d4438011ac1fee7dcab58d
    resource: repo://loader.py
  - id: openwiki-source-833e692518af9eeaf8564cc6
    resource: repo://main.py
  - id: openwiki-source-d37a7a6f6bf2bc7a45be6269
    resource: repo://rag.py
generated: { by: "openwiki/0.4.3", at: "2026-09-01T11:19:44.752Z" }
---

# External service integrations

The backend (`main.py`, `agent.py`, `loader.py`, `rag.py`) integrates with a small set of external libraries and services rather than remote infrastructure. The only true network dependency is Google Gemini; everything else is a Python library operating on a local workbook or local vector store. This page documents each integration boundary, the contract it depends on, and how the pieces are wired together.

## Inventory at a glance

| Integration | Where used | Surface |
| --- | --- | --- |
| Google Gemini | `main.py`, `agent.py` | `ChatGoogleGenerativeAI` — `gemini-2.5-flash` for `/ask`, `gemini-2.5-pro` for the agent; key from `GEMMA_API_KEY` |
| ChromaDB | `rag.py` (write), `main.py` + `agent.py` (read) | `langchain_chroma.Chroma` persisted to `./chroma_db` |
| pandas / OpenPyXL | `loader.py`, `agent.py` tools | `pd.read_excel(file_path, sheet_name=...)` against `data/stats.xlsx` (`FILE_PATH`) |
| FastAPI / CORS | `main.py` | `FastAPI` app + `CORSMiddleware` for `http://localhost:3000` |
| LangChain / LangGraph | `agent.py` | `create_agent` with `MemorySaver` checkpointer; 13 `@tool` functions |
| thefuzz | `main.py`, `agent.py` | `fuzz.partial_ratio` (>80) in `/ask`; `process.extractOne` (>70) in tools |
| GitHub Actions | `.github/workflows/openwiki-update.yml` | Scheduled + dispatch OpenWiki documentation refresh |

## Google Gemini

Gemini is the sole external LLM and the only integration that requires network access and a secret. It is used in two distinct modes through LangChain's `ChatGoogleGenerativeAI`:

- **`/ask` path (`main.py`)** constructs `ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMMA_API_KEY"))`, wraps it in an `llm | StrOutputParser` chain, and invokes that chain with a context-augmented prompt to produce a short answer. Flash is chosen for fast, cheap grounded retrieval.
- **Agent path (`agent.py`)** constructs `ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=os.getenv("GEMMA_API_KEY"))` and passes it to `create_agent`. Pro is used for the longer multi-tool research loop the agent's `system_prompt` orchestrates.

The model split is deliberate and tied to each path's workload: Flash for a single retrieval-grounded generation, Pro for tool-driven multi-step reasoning.

Both modules read the key from the environment variable `GEMMA_API_KEY` (note the spelling: `GEMMA`, not `GEMINI`). `load_dotenv()` loads `.env` in each module, so the key is expected in a local `.env` file during development. There is no key fallback and no other authentication mechanism.

## ChromaDB (local vector store)

ChromaDB is a local on-disk artifact, not a remote service. A single persisted directory `./chroma_db` is shared by three modules:

- **Writer (`rag.py`)** — the offline indexer. It collects `Document` objects from `loader.load_excel_data` for six sheet labels, then calls `Chroma.from_documents(documents=all_docs, persist_directory="./chroma_db")` to build the store.
- **`/ask` reader (`main.py`)** — opens the existing store with `Chroma(persist_directory="./chroma_db")` at startup and runs `similarity_search` and filtered `similarity_search` against it.
- **Agent tools (`agent.py`)** — opens the same store with `Chroma(persist_directory="./chroma_db")`; only `search_regions` and `compare_regions` use it, via `similarity_search` with a `$and` metadata filter on `region`/`indicator`/`era`.

Because all three point at the same `./chroma_db` path, the store is a shared contract: `rag.py` must have been run to populate it, and the metadata field names it writes (`region`, `indicator`, `era`, `source`) are what the readers filter on. There is no runtime embedding step — if the workbook changes, `python rag.py` must be rerun or the index is stale. See [Architecture overview](../architecture/overview.md) for the data-flow diagram.

## pandas / OpenPyXL workbook contract

The Excel workbook is the system's source of truth and the strictest integration contract. pandas (`pd.read_excel`) reads it, which in turn uses OpenPyXL for `.xlsx` parsing. The contract has two layers that must stay in sync.

### Sheet-name contract

`rag.py` enumerates exactly six sheet labels and passes each to `loader.load_excel_data`:

```
"Normal Οικον Βάση"
"Normal Οικον Βάση - Crisis"
"Normal Οικον Βάση - COVID"
"Normal Κοινων Βάση"
"Normal Κοινων Βάση - Crisis"
"Normal Κοινων Βάση - COVID"
```

The agent tools reference these same labels (and the `- Crisis` / `- COVID` variants) by name when calling `pd.read_excel(file_path, sheet_name=...)`. Renaming a sheet breaks both indexing and every tool that targets that sheet.

### Column-label contract

After each `read_excel`, both `loader.py` and the agent tools normalize column headers with `[' '.join(c.split()) for c in df.columns]` — collapsing internal whitespace — and then index into specific columns. The tools depend on fixed, named columns, including:

- `Resistance (2008-2013)`, `Recovery (2013-2019)`, `Recovery (2020-2022)`, `Resistance (2019-2020)`
- `Pre-Crisis (2005-2008)`, `Pre-Crisis (2017-2019)`
- `% Regional Change 2013-2019`, `% National Change 2013-2019`, `% National Change 2008-2013`, `% National Change 2019-2020`, `% National Change 2020-2021`
- `Σύνθετος Οικονομικός Δείκτης`, `Σύνθετος Κοινωνικός Δείκτης`, `RTI_Composite`
- A leading region-name column (the first column), with the national row identified by the literal value `Ελλάδα`.

The workbook location comes from `FILE_PATH` (default `data/stats.xlsx`). If the workbook is absent, every `pd.read_excel` call fails; if a sheet or column label drifts, tools silently misbehave or raise `KeyError`.

## FastAPI and CORS

`main.py` is a FastAPI app exposing `POST /ask` and `POST /agent`, each accepting a `Question` (`{ question: str }`) Pydantic body and returning `{ "answer": str }`. It is served locally with `uvicorn main:app --reload` (port 8000 by convention).

The cross-origin integration with the Next.js frontend is the load-bearing CORS configuration:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- `allow_origins` is pinned to the single origin `http://localhost:3000`, the Next.js dev-server origin. The frontend (`greek_resilient_rag/app/page.tsx`) hard-codes `http://localhost:8000/agent` as its fetch target, so the allowed origin and the fetch target are a matched pair — changing either one independently breaks the cross-origin POST.
- `allow_methods=["*"]` and `allow_headers=["*"]` permit the `POST` with `Content-Type: application/json` the frontend issues.

The frontend performs the cross-origin POST directly from the browser (there is no server-side proxy), so this CORS policy is required, not incidental. See [Next.js frontend](../architecture/frontend.md) for the frontend side of this coupling.

## LangChain and LangGraph

LangChain provides the chat-model wrappers (`ChatGoogleGenerativeAI`), the tool decorator (`@tool`), the document type (`langchain_core.documents.Document`), and the output parser (`StrOutputParser`) used by the `/ask` chain. LangGraph provides the agent runtime and checkpointer.

The agent integration surface in `agent.py` is:

```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
...
agent = create_agent(llm, tools=available_tools, system_prompt=system_prompt, checkpointer=memory)
```

- `create_agent` (from `langchain.agents`) wires the `gemini-2.5-pro` LLM, the 13 `@tool`-decorated functions, the `system_prompt`, and a `MemorySaver` checkpointer into the runnable `agent`.
- `MemorySaver` (from `langgraph.checkpoint.memory`) is an in-process checkpointer. `main.py` invokes the agent with `config={"configurable": {"thread_id": "research-session-3"}}`, so conversational continuity exists within a running process but is not persisted across restarts.

The 13 tool functions registered in `available_tools` are the integration surface the agent can call:

1. `search_regions` — ChromaDB `similarity_search` with `region`/`indicator`/`era` metadata filter.
2. `compare_regions` — invokes `search_regions` twice for two regions.
3. `calculate_percent_change` — reads `Normal Οικον Βάση`, computes percent change between two years.
4. `calculate_resilience_score` — reads a crisis/COVID sheet, classifies Transformative/Adaptive/Vulnerable.
5. `calculate_rti_score` — reads `Normal Οικον Βάση`/`Normal Κοινων Βάση`, trajectory-divergence classification.
6. `calculate_recovery_speed` — recovery speed vs national and median regional rates.
7. `analyze_socioeconomic_coupling` — compares economic vs social recovery ratios.
8. `calculate_structural_shift` — adaptive-cycle trait analysis across pre-crisis/crisis/COVID windows.
9. `save_finding` — appends a finding to `findings.md`.
10. `read_findings` — reads `findings.md`.
11. `calculate_rtix_score` — RTIx score with vulnerability normalization.
12. `calculate_crisis_comparison` — learning-effect comparison of 2008 vs 2019 resistance.
13. `calculate_vulnerability_index` — composite vulnerability from financial and COVID shocks.

The first two read ChromaDB; the rest read the workbook directly with pandas. Adding or removing a `@tool` function changes what the agent can do and is the primary extension point for the agent's analytical capability.

## thefuzz fuzzy matching

`thefuzz` (backed by `RapidFuzz`) softens user input against the exact labels in the workbook and the index. It is used in two distinct ways:

- **`main.py` (`/ask`)** imports `fuzz` and uses `fuzz.partial_ratio(region.lower(), question_lower)` with a threshold of **80** to detect whether any of 13 hard-coded Greek region names appears in the question. When a region scores above 80 and is not already in the result set, it triggers an extra filtered `similarity_search(filter={"region": region})` to enrich the context.
- **`agent.py` (tools)** imports `process` and uses `process.extractOne(region, available_regions)` (and the same for indicators) with a score threshold of **70**. If the best match scores above 70, the user-supplied region/indicator name is replaced with the matched workbook label before querying.

The thresholds differ by design: the `/ask` path is more conservative (80) because it is triggering extra retrieval, while the agent tools are more permissive (70) because the downstream `pd.read_excel` and metadata filters still need an exact label. In both cases fuzzy matching only resolves user phrasing to existing labels — the underlying workbook columns and ChromaDB metadata filters remain exact matches.

## GitHub Actions

The repository has a single remaining workflow, `.github/workflows/openwiki-update.yml`, named "OpenWiki Update". It is the only GitHub Actions integration and is not part of the application runtime.

- **Triggers** — `workflow_dispatch` (manual) plus a `schedule` cron of `0 6 1 * *` (06:00 UTC on the 1st of each month).
- **Permissions** — `contents: write` and `pull-requests: write`, so it can open a documentation update PR.
- **Checkout** — uses `actions/checkout@v4` with the `OPENWIKI_PAT` secret and `fetch-depth: 0`, because OpenWiki needs full history to compute what changed since the last run.
- **Toolchain** — sets up Node.js 22, installs OpenWiki globally (`npm install --global openwiki`), and runs `openwiki code --update --print` with `OPENWIKI_PROVIDER=openrouter`, an `OPENROUTER_API_KEY`, and `OPENWIKI_MODEL_ID=z-ai/glm-5.2`.
- **PR creation** — uses `peter-evans/create-pull-request@v7` (pinned by SHA) on the `openwiki/update` branch, committing changes under `openwiki`, `AGENTS.md`, `CLAUDE.md`, and the workflow file itself.

There is no `tests.yml` or other CI workflow; the only workflow is this scheduled documentation refresh.

## Relationship to other pages

- [Architecture overview](../architecture/overview.md) — the end-to-end data flow from workbook through `rag.py`/`loader.py` into ChromaDB, and the split between the `/ask` RAG path and the `/agent` tool-driven path.
- [Next.js frontend](../architecture/frontend.md) — the `http://localhost:3000` ↔ `http://localhost:8000` CORS pairing from the frontend side.
- [Operations / runbook](../operations/runbook.md) — `GEMMA_API_KEY`, `FILE_PATH`, rebuilding `./chroma_db`, and the sheet/column drift failure modes.
- [Workflows / usage](../workflows/usage.md) — the indexing and query workflows that exercise these integrations.
