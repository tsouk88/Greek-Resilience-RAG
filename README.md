## Greek Regional Resilience RAG

A RAG system for querying and analyzing Greek regional economic and social resilience indicators using FastAPI, ChromaDB, LangChain and Gemini AI.

## What it does
Answers questions about Greek regional economic and social data (2005-2022) using AI. Features:
- Natural language queries in Greek or English
- Multi-region comparisons with fuzzy region name matching
- Research agent with tools for targeted search, region comparison, and % change calculations
- Two endpoints: `/ask` for quick RAG queries, `/agent` for complex research analysis

## Tech Stack
- FastAPI
- ChromaDB (local embeddings)
- LangChain + LangGraph
- Google Gemini API (gemini-2.5-flash)
- pandas
- thefuzz (fuzzy matching)

## Setup
1. Clone the repo
2. Create virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\activate`
4. Install: `pip install -r requirements.txt`
5. Add your `.env` file with `GEMMA_API_KEY=your_key`
6. Add your Excel data file to `data/stats.xlsx`
7. Run embeddings: `python rag.py`
8. Start server: `uvicorn main:app --reload`

## Endpoints
POST `/ask` — quick RAG query:
```json
{"question": "Συγκρινε την Αττική με τη Θεσσαλία"}
```
POST `/agent` — research agent with tools:
```json
{"question": "Ποσοστό μεταβολής απασχόλησης Βόρειο vs Νότιο Αιγαίο 2005-2022"}
```