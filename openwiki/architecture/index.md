# Files

- [Next.js frontend](frontend.md) - The greek_resilient_rag Next.js 16 app-router frontend: a single client chat page that posts questions to the backend /agent endpoint over CORS, with its layout, scripts, and toolchain.
- [Architecture overview](overview.md) - System shape of the FastAPI backend and Next.js frontend, the two API paths (POST /ask RAG and POST /agent tool-driven), and the data flow from the Excel workbook through loader/rag into ChromaDB and through the agent tools.
