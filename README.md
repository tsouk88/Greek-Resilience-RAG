# Greek Regional Economic Resilience RAG

A RAG system for querying and analyzing Greek regional economic indicators using AI.

## What it does
Answers questions about Greek regional economic data (2005-2023) using AI. Supports comparisons between regions across three periods: Expansion, Crisis, and Recovery.

## Tech Stack
- FastAPI
- ChromaDB
- LangChain
- Google Gemini API
- pandas

## Setup
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install: `pip install -r requirements.txt`
5. Add your `.env` file with `GEMMA_API_KEY=your_key`
6. Add your Excel data file to `data/`
7. Run embeddings: `python rag.py`
8. Start server: `uvicorn main:app --reload`

## Usage
POST `/ask` with:
```json
{"question": "Συγκρινε την Αττική με την Ελλάδα"}
```