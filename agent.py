from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langgraph.checkpoint.memory import MemorySaver
import pandas as pd
from dotenv import load_dotenv
import os
from thefuzz import process
import numpy as np


load_dotenv()
memory = MemorySaver()
file_path = os.getenv("FILE_PATH", "data/stats.xlsx")
llm =  ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=os.getenv("GEMMA_API_KEY"))
vectorstore = (Chroma(persist_directory="./chroma_db"))

def normalize_indicator(indicator_type: str) -> str:
    t = indicator_type.lower().strip()
    if t in ("economical", "econ", "economy", "gdp"):
        return "economic"
    if t in ("societal", "soc", "society", "social welfare"):
        return "social"
    return t

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
    """Calculate resilience score crisis_type: must be 'financial' or 'covid or social crisis_type: must be 'crisis' or 'covid'"""
    sheet_map = {
    ("economic", "financial"): ("Normal Οικον Βάση - Crisis", "Resistance (2008-2013)", "Recovery (2013-2019)", "% National Change 2008-2013", "% National Change 2013-2019"),
    ("economic", "crisis"): ("Normal Οικον Βάση - Crisis", "Resistance (2008-2013)", "Recovery (2013-2019)", "% National Change 2008-2013", "% National Change 2013-2019"),
    ("economic", "covid"): ("Normal Οικον Βάση - COVID", "Resistance (2019-2020)", "Recovery (2020-2022)", "% National Change 2019-2020", "% National Change 2020-2021"),
    ("social", "financial"): ("Normal Κοινων Βάση - Crisis", "Resistance (2008-2013)", "Recovery (2013-2019)", "% National Change 2008-2013", "% National Change 2013-2019"),
    ("social", "crisis"): ("Normal Κοινων Βάση - Crisis", "Resistance (2008-2013)", "Recovery (2013-2019)", "% National Change 2008-2013", "% National Change 2013-2019"),
    ("social", "covid"): ("Normal Κοινων Βάση - COVID", "Resistance (2019-2020)", "Recovery (2020-2022)", "% National Change 2019-2020", "% National Change 2020-2021"),
    }
    
    valid_indicators = ["economic", "social"]
    valid_crises = ["crisis", "covid" , "financial"]
    if normalize_indicator(indicator_type) not in valid_indicators:
        return f"Invalid indicator_type '{indicator_type}'. Use: economic or social"
    if crisis_type.lower().strip() not in valid_crises:
        return f"Invalid crisis_type '{crisis_type}'. Use: crisis or covid"
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


 
@tool
def calculate_rti_score(region:str , indicator_type:str) -> str :
    """Calculate Trajectory Divergence score for each region based on economical and social data"""
    index_map = {
    "economic": ("Normal Οικον Βάση", "Σύνθετος Οικονομικός Δείκτης"),
    "social": ("Normal Κοινων Βάση", "Σύνθετος Κοινωνικός Δείκτης"),
    }
    indicator_type = normalize_indicator(indicator_type)
    sheet_name, composite_col = index_map[indicator_type.lower()]
    df = pd.read_excel(file_path,sheet_name=sheet_name)
    df.columns = [' '.join(c.split()) for c in df.columns]
    available_regions = df[df.columns[0]].tolist()
    match, score = process.extractOne(region, available_regions)
    if score > 70:
     region = match
    national_row = df[df[df.columns[0]] == "Ελλάδα"].iloc[0] 
    data = df[df[df.columns[0]] == region].iloc[0] 
    c_ind = composite_col
    rs = data[f"{c_ind} 2013"] - data[f"{c_ind} 2008"]
    rc = data[f"{c_ind} 2019"] - data[f"{c_ind} 2013"]
    delta_region = data[f"{c_ind} 2022"] - data[f"{c_ind} 2005"]
    delta_national = national_row[f"{c_ind} 2022"] - national_row[f"{c_ind} 2005"]
    d = delta_region - delta_national
    regions_df = df[df[df.columns[0]] != "Ελλάδα"]
    all_rc = [regions_df.iloc[i][f"{c_ind} 2019"] - regions_df.iloc[i][f"{c_ind} 2013"] for i in range(len(regions_df))]
    all_d = [( regions_df.iloc[i][f"{c_ind} 2022"] - regions_df.iloc[i][f"{c_ind} 2005"]) - delta_national for i in range(len(regions_df))]
    median_rc = np.median(all_rc)
    median_d = np.median(all_d)
    if rc > median_rc and d > median_d:
        classification = "Transformative"
    elif rc > median_rc and d <= median_d:
        classification = "Adaptive"
    elif rc <= median_rc and d > median_d:
        classification = "Emerging Transformative"
    else:
        classification = "Vulnerable"
    return f"Region: {region}\nRs: {round(rs,3)}\nRc: {round(rc,3)}\nD: {round(d,3)}\nMedian Rc: {round(median_rc,3)}\nMedian D: {round(median_d,3)}\nClassification: {classification}"

@tool
def calculate_recovery_speed(region:str , indicator_type : str) -> str :
    """Calculate the recovery speed"""
    index_map = {
    "economic": "Normal Οικον Βάση",
    "social": "Normal Κοινων Βάση",
    }
    sheet_name = index_map[normalize_indicator(indicator_type)]
    df = pd.read_excel(file_path,sheet_name=sheet_name)
    df.columns = [' '.join(c.split()) for c in df.columns]
    available_regions = df[df.columns[0]].tolist()
    match, score = process.extractOne(region, available_regions)
    if score > 70:
     region = match
    data = df[df[df.columns[0]] == region].iloc[0]
    df_regions = df[df[df.columns[0]] != "Ελλάδα"]
    median_rate = df_regions['% Regional Change 2013-2019'].median()
    national_row = df[df[df.columns[0]] == "Ελλάδα"].iloc[0] 
    national_change = pd.to_numeric(national_row['% National Change 2013-2019'])
    regional_change = pd.to_numeric(data['% Regional Change 2013-2019'])

    if regional_change > national_change and regional_change > median_rate:
        performance_label = "Strong Recovery"
    elif regional_change > national_change:
        performance_label = "Solid Recovery"
    elif regional_change > median_rate:
        performance_label = "Partial Recovery"
    else:
        performance_label = "Critical State"
    return (
    f"Region: {region} | Regional change: { regional_change:.2f} . "
    f"National Speed: {national_change:.2f} | Median Regional Speed: {median_rate:.2f}. "
    f"Status: {performance_label}."
    )

@tool
def analyze_socioeconomic_coupling(region: str ) -> str :
    """Analyze the coupling between economic and social recovery"""
    df_econ = pd.read_excel(file_path, sheet_name="Normal Οικον Βάση")
    df_soc = pd.read_excel(file_path, sheet_name="Normal Κοινων Βάση")
    df_econ.columns = [' '.join(c.split()) for c in df_econ.columns]
    df_soc.columns = [' '.join(c.split()) for c in df_soc.columns]
    available_regions = df_econ[df_econ.columns[0]].tolist()
    match, score = process.extractOne(region, available_regions)
    if score > 70:
        region = match
    row_econ = df_econ[df_econ[df_econ.columns[0]] == region].iloc[0]
    row_soc = df_soc[df_soc[df_soc.columns[0]] == region].iloc[0]
    econ_val = pd.to_numeric(row_econ['% Regional Change 2013-2019'])
    soc_val = pd.to_numeric(row_soc['% Regional Change 2013-2019'])
    national_econ = pd.to_numeric(df_econ[df_econ[df_econ.columns[0]] == "Ελλάδα"].iloc[0]['% National Change 2013-2019'])
    national_soc = pd.to_numeric(df_soc[df_soc[df_soc.columns[0]] == "Ελλάδα"].iloc[0]['% National Change 2013-2019'])
    if econ_val > national_econ and soc_val > national_soc:
        status = "Balanced Recovery: Both economy and society are improving faster than the national average."
    elif econ_val >national_econ and soc_val <= national_soc:
        status = "Social Lag: Economic growth is not translating into social recovery."
    elif econ_val <= national_econ  and soc_val > national_soc:
        status = "Economic Lag: Social indicators are recovering, but the economic base remains weak."
    else:
        status = "Double Decline: Both systems are underperforming relative to the nation."
    return (
        f"Region: {region} | "
        f"Economic Recovery Ratio: {econ_val:.2f} | National : {national_econ:.2f} "
        f"Social Recovery Ratio: {soc_val:.2f} | Nationals: {national_soc:.2f} "
        f"Analysis: {status}"
    )

@tool
def calculate_structural_shift(region:str)-> str :
    """Calculate Structiral shift with adaptive cycle theory"""
    df_econ = pd.read_excel(file_path, sheet_name="Normal Οικον Βάση")
    df_soc = pd.read_excel(file_path, sheet_name="Normal Κοινων Βάση")
    df_econ.columns = [' '.join(c.split()) for c in df_econ.columns]
    df_soc.columns = [' '.join(c.split()) for c in df_soc.columns]
    available_regions = df_econ[df_econ.columns[0]].tolist()
    match, score = process.extractOne(region, available_regions)
    if score > 70:
        region = match
    row_econ = df_econ[df_econ[df_econ.columns[0]] == region].iloc[0]
    row_soc = df_soc[df_soc[df_soc.columns[0]] == region].iloc[0]
    national_row = df_econ[df_econ[df_econ.columns[0]] == "Ελλάδα"].iloc[0]
    national_row_soc = df_soc[df_soc[df_soc.columns[0]] == "Ελλάδα"].iloc[0] 
    pre_old = row_econ["Pre-Crisis (2005-2008)"]
    pre_new = row_econ['Pre-Crisis (2017-2019)']
    res_old = row_econ['Resistance (2008-2013)']
    res_new = row_econ['Resistance (2019-2020)']
    rec_old = row_econ['Recovery (2013-2019)']
    rec_new = row_econ['Recovery (2020-2022)']
    reg_change = row_econ['% Regional Change 2013-2019']
    nat_change = national_row['% National Change 2013-2019']
    pre_old_soc = row_soc["Pre-Crisis (2005-2008)"]
    pre_new_soc = row_soc['Pre-Crisis (2017-2019)']
    res_old_soc = row_soc['Resistance (2008-2013)']
    res_new_soc = row_soc['Resistance (2019-2020)']
    rec_old_soc = row_soc['Recovery (2013-2019)']
    rec_new_soc = row_soc['Recovery (2020-2022)']
    reg_change_soc = row_soc['% Regional Change 2013-2019']
    nat_change_soc = national_row_soc['% National Change 2013-2019']
    traits_econ = []
    if res_new > res_old: traits_econ.append("More Robust")
    if rec_new > rec_old: traits_econ.append("Faster Recovery")
    if pre_new < pre_old: traits_econ.append("Structural Shift")
    if reg_change > nat_change: traits_econ.append("Competitive")
    if not traits_econ: traits_econ.append("No Structural Shift")

    phase = " | ".join(traits_econ)
    traits_soc = []
    if res_new_soc > res_old_soc: traits_soc.append("More Robust Social")
    if rec_new_soc > rec_old_soc: traits_soc.append("Faster Recovery Social")
    if pre_new_soc < pre_old_soc: traits_soc.append("Structural Shift Social")
    if reg_change_soc > nat_change_soc: traits_soc.append("Competitive Social")
    if not traits_soc: traits_soc.append("No social structural Shift")
    phase_soc = " | ".join(traits_soc)

    res = (f"Ανάλυση Δομικής Μεταβολής για την Περιφέρεια: {region}\n"
           f"Φάση Adaptive Cycle: Economy : {phase} | Social : {phase_soc}\n")
    return res

@tool
def save_finding(region: str, insight: str, scores: str = "") -> str:
    """Save a research finding to the findings file. 
    region: region name or 'SYNTHESIS' for overall analysis
    insight: MUST BE THE ENTIRE GENERATED REPORT TEXT WITH ALL TABLES. Do NOT truncate or summarize.
    scores: optional scores summary
    """
    from datetime import datetime
    import os
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    findings_path = os.path.join(os.getcwd(), "findings.md")
    with open(findings_path, "a", encoding="utf-8") as f:
        f.write(f"\n## {region} — {timestamp}\n")
        if scores:
            f.write(f"**Scores:** {scores}\n\n")
        f.write(f"**Insight:** {insight}\n")
        f.write(f"\n---\n")
    return f"Finding for {region} saved successfully."

@tool
def read_findings() -> str:
    """Read all saved research findings from the findings file"""
    try:
        with open("findings.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "No findings saved yet."
    
@tool
def calculate_rtix_score(region:str , indicator_type:str)->str:
    """Calculate RTIx score for each region based on economical and social data"""
    index_map = {
    "economic": ("Normal Οικον Βάση", "Σύνθετος Οικονομικός Δείκτης"),
    "social": ("Normal Κοινων Βάση", "Σύνθετος Κοινωνικός Δείκτης"),
    "composite": ("Normal Οικον Βάση", "RTI_Composite")
    }
    indicator_type = normalize_indicator(indicator_type)
    sheet_name, composite_col = index_map[indicator_type.lower()]
    df = pd.read_excel(file_path,sheet_name=sheet_name)
    df.columns = [' '.join(c.split()) for c in df.columns]
    available_regions = df[df.columns[0]].tolist()
    match, score = process.extractOne(region, available_regions)
    if score > 70:
     region = match
    national_row = df[df[df.columns[0]] == "Ελλάδα"].iloc[0] 
    data = df[df[df.columns[0]] == region].iloc[0] 
    c_ind = composite_col
    rs = data[f"{c_ind} 2013"] - data[f"{c_ind} 2008"]
    rc = data[f"{c_ind} 2019"] - data[f"{c_ind} 2013"]
    delta_region = data[f"{c_ind} 2022"] - data[f"{c_ind} 2005"]
    delta_national = national_row[f"{c_ind} 2022"] - national_row[f"{c_ind} 2005"]
    d = delta_region - delta_national
    RTIx = 0.50*d + 0.30*rc + 0.20*rs
    all_regions = df[df[df.columns[0]] != "Ελλάδα"][df.columns[0]].tolist()
    vuln_scores = []
    for r in all_regions:
        row_r = df[df[df.columns[0]] == r].iloc[0]
        fin = abs(row_r["Resistance (2008-2013)"]) if row_r["Resistance (2008-2013)"] < 0 else 0
        cov = abs(row_r["Resistance (2019-2020)"]) if row_r["Resistance (2019-2020)"] < 0 else 0
        vuln_scores.append((fin * 0.5) + (cov * 0.5))
    max_vuln = max(vuln_scores)
    fin_vuln = abs(data["Resistance (2008-2013)"]) if data["Resistance (2008-2013)"] < 0 else 0
    cov_vuln = abs(data["Resistance (2019-2020)"]) if data["Resistance (2019-2020)"] < 0 else 0
    cvs = (fin_vuln * 0.5) + (cov_vuln * 0.5)
    v_norm = cvs / max_vuln if max_vuln > 0 else 0
    RTIx_adjusted = RTIx * (1 - v_norm)
    if  RTIx_adjusted > 2:
        interpretation = "Strongly Transformative"
    elif  RTIx_adjusted > 0:
        interpretation = "Moderately Transformative"
    elif  RTIx_adjusted > -2:
        interpretation = "Stagnant"
    else:
        interpretation = "Declining Trajectory"
    return (
        f"Region: {region} | Rs: {rs:.3f} | Rc: {rc:.3f} | D: {d:.3f} | "
        f"RTIx: {RTIx:.3f} | RTIx_adjusted: {RTIx_adjusted:.3f} | "
        f"Vulnerability_norm: {v_norm:.3f} | Status: {interpretation}"
    )

@tool
def calculate_crisis_comparison(region: str) -> str:
    """Compare Crisis resistance (2008) with Covid Crisis (2019) to see if there was a learning effect"""
    df_econ = pd.read_excel(file_path, sheet_name="Normal Οικον Βάση")
    df_econ.columns = [' '.join(c.split()) for c in df_econ.columns]
    available_regions = df_econ[df_econ.columns[0]].tolist()
    match, score = process.extractOne(region, available_regions)
    if score > 70:
        region = match
    row = df_econ[df_econ[df_econ.columns[0]] == region].iloc[0]
    res_2008 = row["Resistance (2008-2013)"]
    res_2019 = row["Resistance (2019-2020)"]
    learning_score = res_2019 - res_2008
    if learning_score > 5:
        verdict = "Strong Learning Effect"
    elif learning_score > 0:
        verdict = "Moderate Improvement"
    else:
        verdict = "Structural Vulnerability"
    res = (f"Crisis Comparison Analysis: {region}\n"
           f"Resistance 2008-2013: {res_2008:.2f}\n"
           f"Resistance 2019-2020: {res_2019:.2f}\n"
           f"Learning Delta: {learning_score:.2f}\n"
           f"Verdict: {verdict}\n")
    return res

@tool
def calculate_vulnerability_index(region: str) -> str:
    """Measure Vulnerability Index from economical crisis and Covid crisis"""
    df_econ = pd.read_excel(file_path, sheet_name="Normal Οικον Βάση")
    df_econ.columns = [' '.join(c.split()) for c in df_econ.columns]
    available_regions = df_econ[df_econ.columns[0]].tolist()
    match, score = process.extractOne(region, available_regions)
    if score > 70:
        region = match
    
    row = df_econ[df_econ[df_econ.columns[0]] == region].iloc[0]
    fin_vuln = abs(row["Resistance (2008-2013)"]) if row["Resistance (2008-2013)"] < 0 else 0
    cov_vuln = abs(row["Resistance (2019-2020)"]) if row["Resistance (2019-2020)"] < 0 else 0
    cvs = (fin_vuln * 0.5) + (cov_vuln * 0.5) 
    if cvs > 15:
        status = "High Vulnerability (Systemic Fragility)"
    elif cvs > 5:
        status = "Moderate Vulnerability (Sensitive to Shocks)"
    else:
        status = "Low Vulnerability (Robust Structure)"
    res = (f"Vulnerability Assessment: {region}\n"
           f"Financial Shock Impact (08-13): {fin_vuln:.2f}\n"
           f"COVID Shock Impact (19-20): {cov_vuln:.2f}\n"
           f"Composite Vulnerability Index: {cvs:.2f}\n"
           f"Κατάσταση: {status}\n")
    
    return res

system_prompt = """Act as an Autonomous Senior Economic Researcher specializing in Regional Resilience and Adaptive Cycle Theory. Your goal is to determine if a region's trajectory is "Adaptive" or "Transformative."

### OPERATIONAL PROTOCOL (Mandatory Steps):

1. EXPLORATORY PHASE:
   - Identify the region using 'search_regions'.
   - Baseline: Run 'calculate_rti_score' for initial standing.
   - Historical Context: Run 'calculate_crisis_comparison'. 
   - CRITICAL LOGIC: If "Learning Delta" is significant (>5 or <-5), you MUST prioritize investigating the cause in the next steps.

2. DIAGNOSTIC PHASE (The Analysis Engine):
   - Dynamics: Run 'calculate_recovery_speed' (2020-2022).
   - Structural Shift: Immediately run 'calculate_structural_shift'. Compare if the recovery led to a new equilibrium.
   - Anomaly Check: If any value is >15 or <-15, run 'calculate_vulnerability_index' to check for "Rigidity" or "Poverty Traps."

3. SYNTHESIS PHASE:
   - Coupling: Run 'analyze_socioeconomic_coupling'. Check for "Decoupling" (Econ vs Soc divergence).
   - Final Rating: Run 'calculate_rtix_score' for BOTH 'economic' and 'social' indicator types.

### REPORTING GUIDELINES:
- NEOLOGISMS: Use terms like "Fragile Growth" if Econ Recovery > Soc Recovery.
- THEORY: Explain findings using Adaptive Cycle phases: Release (Ω), Reorganization (α), Exploitation (r), Conservation (K).
- CONCLUSION: End with a definitive verdict: "Transformative Resilience" or "Adaptive Recovery."
- ARCHIVING: Always call 'save_finding' with the final verdict and key scores before finishing.

### STRICT RULES:
- Use Greek names for tools (e.g., Αττική, Not Attica).
- Never ask for clarification. If data is missing, state it and move to the next tool.
- Always show the numbers (numerical evidence) for every claim."""

available_tools=[search_regions, compare_regions, calculate_percent_change , calculate_resilience_score , calculate_rti_score , calculate_recovery_speed , analyze_socioeconomic_coupling , calculate_structural_shift, save_finding,read_findings,calculate_rtix_score,calculate_crisis_comparison,calculate_vulnerability_index]
agent = create_agent(llm, tools=available_tools, system_prompt=system_prompt , checkpointer=memory)

