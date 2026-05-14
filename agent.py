from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langgraph.checkpoint.memory import MemorySaver
import pandas as pd
from dotenv import load_dotenv
import os
from thefuzz import process


load_dotenv()
memory = MemorySaver()
file_path = os.getenv("FILE_PATH", "data/stats.xlsx")
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
    df = pd.read_excel(file_path, 
                   sheet_name="Normal Οικον Βάση")
    df.columns = [' '.join(c.split()) for c in df.columns]
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

@tool
def calculate_resilience_score(region: str, indicator_type: str = "economic", crisis_type: str = "financial") -> str:
    """Calculate resilience score and classification for a Greek region based on crisis resistance and recovery data."""
    sheet_map = {
    ("economic", "financial"): ("Normal Οικον Βάση - Crisis", "Resistance (2008-2013)", "Recovery (2013-2019)", "% National Change 2008-2013", "% National Change 2013-2019"),
    ("economic", "covid"): ("Normal Οικον Βάση - COVID", "Resistance (2019-2020)", "Recovery (2020-2022)", "% National Change 2019-2020", "% National Change 2020-2021"),
    ("social", "financial"): ("Normal Κοινων Βάση - Crisis", "Resistance (2008-2013)", "Recovery (2013-2019)", "% National Change 2008-2013", "% National Change 2013-2019"),
    ("social", "covid"): ("Normal Κοινων Βάση - COVID", "Resistance (2019-2020)", "Recovery (2020-2022)", "% National Change 2019-2020", "% National Change 2020-2021"),
    }
    sheet_name, res_col, rec_col, nat_res_col, nat_rec_col = sheet_map[(indicator_type.lower(), crisis_type.lower())]
    df = pd.read_excel(file_path,sheet_name=sheet_name)
    df.columns = [' '.join(c.split()) for c in df.columns]
    available_regions = df[df.columns[0]].tolist()
    match, score = process.extractOne(region, available_regions)
    if score > 70:
     region = match
    national_row = df[df[df.columns[0]] == "Ελλάδα"].iloc[0]
    data = df[df[df.columns[0]] == region].iloc[0]
    res=data[res_col]
    rec=data[rec_col]
    resilience_score = res + rec
    nat_res = national_row[nat_res_col]
    nat_rec = national_row[nat_rec_col]
    nat_score = nat_res + nat_rec
    if res > nat_res and rec > nat_rec:
        classification = "Transformative"
    elif res > nat_res or rec > nat_rec:
        classification = "Adaptive"
    else:
        classification = "Vulnerable"
    return f"{resilience_score}\n{nat_score}\n{classification}" 


system_prompt = """You are a regional economic resilience analyst for Greek regions.
Always use Greek region names when calling tools (e.g. Αττική not Attica, Κρήτη not Crete)
You have tools available - USE THEM immediately without asking for clarification.
When asked to compare two regions, call calculate_percent_change for EACH region separately, then compare the results.
Always show the numbers and your reasoning.
Never ask the user to clarify - make reasonable assumptions and proceed."""

agent = create_agent(llm, tools=[search_regions, compare_regions, calculate_percent_change , calculate_resilience_score ], system_prompt=system_prompt , checkpointer=memory)
