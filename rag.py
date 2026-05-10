
from langchain_chroma import Chroma
from loader import load_excel_data


sheets = [
    "Normal Οικον Βάση",
    "Normal Οικον Βάση - Crisis", 
    "Normal Οικον Βάση - COVID",
    "Normal Κοινων Βάση",
    "Normal Κοινων Βάση - Crisis",
    "Normal Κοινων Βάση - COVID"
]
all_docs = []
for sheet in sheets:
    docs = load_excel_data("C:/Users/tsouk/Desktop/python-practice/PhD-Rag/data/stats.xlsx", sheet)
    all_docs += docs
    print(f"Loaded {len(docs)} chunks from {sheet}")

vectorstore = Chroma.from_documents(
    documents=all_docs,
    persist_directory="./chroma_db"
        )



print(f"Done! Stored {len(all_docs)} chunks.")

