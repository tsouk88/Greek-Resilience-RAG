# Workflows

## Indexing workflow
The repository’s index is built by `rag.py`.
It loads six workbook sheets, converts each sheet with `load_excel_data`, and stores all documents in a local ChromaDB directory named `./chroma_db`.

Typical sequence:
1. Ensure the workbook exists at `FILE_PATH` or `data/stats.xlsx`.
2. Run `python rag.py`.
3. Confirm the script reports how many chunks were loaded per sheet and the total stored chunks.

## Query workflow: `/ask`
`POST /ask` in `main.py` is the quick RAG path.
It:
1. Uses `vectorstore.similarity_search(question, k=10)`.
2. Collects region metadata from the results.
3. Applies fuzzy region-name matching against a curated list of Greek regions.
4. Pulls extra filtered documents for any likely missed region.
5. Sends the combined context to Gemini and returns a short answer.

Use this route for short, factual, workbook-grounded questions.

## Research workflow: `/agent`
`POST /agent` in `main.py` delegates to the LangChain agent defined in `agent.py`.
The agent is backed by workbook-reading tools and a shared memory checkpoint (`MemorySaver`).

Available tool patterns include:
- search a region/indicator/era combination
- compare two regions
- calculate percent change across years
- calculate resilience scores from crisis-specific sheets
- calculate RTI/trajectory-divergence style scores
- analyze socioeconomic coupling and structural shift

Use this route when the answer requires derived metrics, multi-step comparison, or explicit analytical classification.

## Standalone analysis scripts
- `cluster_analysis.py` reproduces the clustering visuals (`cluster_scatter.png`, `cluster_radar.png`) from hard-coded region score data.
- `deepresearch.py` reads the chapter-length source material and asks Gemini to produce a literature synthesis saved to `literature_synthesis.md`.

## Practical notes for future changes
- If you rename sheets or workbook columns, update both `loader.py` and the tool functions in `agent.py`.
- If you change the workbook location, prefer environment-variable support via `FILE_PATH` instead of hard-coding paths.
- If you change the region list or metadata schema, validate the `/ask` fuzzy matching and the tool filters together.
