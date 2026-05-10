from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from loader import load_excel_data
import time

load_dotenv()
batch_size = 50
vectorstore = None

embeddings = GoogleGenerativeAIEmbeddings(
   model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMMA_API_KEY")
)

docs = load_excel_data("C:/Users/tsouk/Desktop/python-practice/PhD-Rag/data/stats.xlsx" , "Normal Οικον Βάση")
for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    print(f"Embedding batch {i//batch_size + 1}...")
    
    if vectorstore is None:
        vectorstore = Chroma.from_documents(
            documents=batch,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
    else:
        vectorstore.add_documents(batch)
    
    time.sleep(90) 

print(f"Done! Stored {len(docs)} chunks.")

