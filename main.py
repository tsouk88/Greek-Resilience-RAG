from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
class Question(BaseModel):
    question: str

app=FastAPI()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMMA_API_KEY"))
parser = StrOutputParser()                           
chain = llm|parser
embeddings = GoogleGenerativeAIEmbeddings(
     model="models/gemini-embedding-001",
    google_api_key=os.getenv("GEMMA_API_KEY")
    )
vectorstore = (Chroma(persist_directory="./chroma_db", 
                      embedding_function=embeddings))
@app.post("/ask") 
async def handle_message(message: Question):
    results = vectorstore.similarity_search(message.question, k=10)
    found_regions = set([r.metadata["region"] for r in results])
    all_results = list(results)
    greek_regions = ["Αττική", "Θεσσαλία", "Κρήτη", "Βόρειο Αιγαίο", 
                     "Κεντρική Μακεδονία", "Δυτική Μακεδονία", "Ήπειρος",
                     "Ιόνια Νησιά", "Δυτική Ελλάδα", "Στερεά Ελλάδα",
                     "Πελοπόννησος", "Νότιο Αιγαίο", "Ανατολική Μακεδονία και Θράκη"]
    question_lower = message.question.lower()
    for region in greek_regions:  
        if region.lower() in question_lower and region not in found_regions:
            extra = vectorstore.similarity_search(
            message.question, k=5,
            filter={"region": region}
        )
            all_results += extra
    context = "\n\n".join([doc.page_content for doc in all_results])
    prompt = f"You are a resilience data analyst . You respond in max 5 sentences. For example if someones asks you what was the data in Αττικη before crisis , you give the data and you compare it to ελλαδα commenting about it  "
    full_prompt = f"""System: {prompt}
    Context:
    {context}
    Question: {message.question}"""
    response = chain.invoke(full_prompt)
    return {"answer": response}
