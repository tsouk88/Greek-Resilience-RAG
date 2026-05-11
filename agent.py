from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
import pandas as pd
from dotenv import load_dotenv
import os
from thefuzz import process

load_dotenv()
llm =  ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMMA_API_KEY"))
vectorstore = (Chroma(persist_directory="./chroma_db"))
@tool
def search_regions(region: str, indicator: str, era : str) -> str: 
    """Search ChromaDB for a specific region, indicator and era and return the relevant data."""
    era_map = {
    "crisis": "Crisis (Κρίση)",
    "expansion": "Expansion (Προ Κρίσης)",
    "recovery": "Recovery (Ανάκαμψη)",
    "κρίση": "Crisis (Κρίση)",
    "ανάκαμψη": "Recovery (Ανάκαμψη)"
        }
    era = era_map.get(era.lower(), era)
    query = f"{region} {indicator} {era}"
    results = vectorstore.similarity_search(query, k=5, filter={
    "$and": [
        {"region": {"$eq": region}},
        {"indicator": {"$eq": indicator}},
        {"era": {"$eq": era}}
    ]
    })
    context = "\n\n".join([doc.page_content for doc in results])
    return context

@tool
def compare_regions(region1:str , region2:str , indicator : str , era : str)-> str :
    """compare does the same for 2 regions and compares them"""
    result1 = search_regions.invoke({"region": region1, "indicator": indicator, "era": era })
    result2 = search_regions.invoke({"region": region2, "indicator": indicator, "era": era })
    return f"{result1}\n\n{result2}"
    

@tool
def calculate_percent_change(region : str, indicator : str, start_year: int, end_year: int) -> float:
    """percentage searchs the raw data and counts it"""
    df = pd.read_excel("C:/Users/tsouk/Desktop/python-practice/PhD-Rag/data/stats.xlsx", 
                   sheet_name="Normal Οικον Βάση")
    available_regions = df[df.columns[0]].tolist()
    match, score = process.extractOne(region, available_regions)
    if score > 70:
     region = match
    available_indicators = sorted(list(set([" ".join(col.split()[:-1]) for col in df.columns[1:]])))
    ind_match, ind_score = process.extractOne(indicator, available_indicators)
    if ind_score > 70:
        indicator = ind_match
    data = df[df[df.columns[0]] == region].iloc[0]
    start =data[f"{indicator} {start_year}"]
    end =data[f"{indicator} {end_year}"]
    percentage = (end - start) / start *100
    return round(percentage, 2)


agent = create_agent(llm, tools=[search_regions, compare_regions, calculate_percent_change]) 
