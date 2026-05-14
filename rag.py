
from langchain_chroma import Chroma
from loader import load_excel_data
import os

file_path = os.getenv("FILE_PATH", "data/stats.xlsx")

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
    docs = load_excel_data(file_path, sheet)
    all_docs += docs
    print(f"Loaded {len(docs)} chunks from {sheet}")

vectorstore = Chroma.from_documents(
    documents=all_docs,
    persist_directory="./chroma_db"
        )



print(f"Done! Stored {len(all_docs)} chunks.")

