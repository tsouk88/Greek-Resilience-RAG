# Source map

## Entry points
- `main.py` — FastAPI app, `/ask`, `/agent`, Gemini setup, ChromaDB loading, CORS
- `rag.py` — offline document ingestion into ChromaDB
- `agent.py` — LangChain tools and analytical scoring functions

## Data shaping
- `loader.py` — workbook-to-document conversion with region/indicator/era metadata
- `test_loader.py` — verifies loader behavior and metadata expectations

## Domain and narrative artifacts
- `findings.md` — long-form analytical notes and RTIx interpretations
- `literature_synthesis.md` — generated literature review in Greek
- `cluster_analysis.py` — cluster scoring and visualization script
- `cluster_scatter.png`, `cluster_radar.png` — generated figures from the cluster script
- `deepresearch.py` — Gemini-driven synthesis generator based on the chapter source document

## Operational files
- `requirements.txt` — dependency set, including FastAPI, LangChain, ChromaDB, pandas, pytest, and plotting/scientific packages
- `.github/workflows/tests.yml` — CI test workflow
- `.github/workflows/openwiki-update.yml` — scheduled documentation refresh workflow

## Change hotspots
When modifying behavior, start with the following code paths:
- workbook schema or location changes: `loader.py`, `rag.py`, `agent.py`, `test_loader.py`
- request/response behavior: `main.py`
- analytical scoring or region classification: `agent.py`, `cluster_analysis.py`, `findings.md`
- narrative generation: `deepresearch.py`, `literature_synthesis.md`

## Notes for future agents
- The repository already contains generated analysis artifacts; treat them as evidence of the project’s intended interpretation, not just incidental output.
- If code and narrative disagree, prefer the current source code and recent git history for implementation details, and use the generated narratives to understand the intended framing.
