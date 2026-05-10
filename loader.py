
from langchain_core.documents import Document
import pandas as pd



def load_excel_data(file_path, sheet_label):
    df = pd.read_excel(file_path, sheet_name=sheet_label)
    df.columns = [c.strip() for c in df.columns]
    national_row = df[df[df.columns[0]] == "Ελλάδα"].iloc[0]
    
    docs = []
    
    eras = {
        "Expansion (Προ Κρίσης)": ["2005", "2006", "2007", "2008"],
        "Crisis (Κρίση)": ["2009", "2010", "2011", "2012", "2013"],
        "Recovery (Ανάκαμψη)": ["2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023"]
    }
    
    indicators = sorted(list(set([" ".join(col.split()[:-1]) for col in df.columns[1:]])))

    for _, row in df.iterrows():
        region_name = row[df.columns[0]]
        if region_name == "Ελλάδα":
            continue
            
        
        for ind in indicators:
            
            for era_name, years in eras.items():
                
                era_values = []
                
                for yr in years:
                    col_name = f"{ind} {yr}"
                    if col_name in row:
                        val = row[col_name]
                        nat_val = national_row[col_name]
                        era_values.append(f"{yr}: {val} (Ελλάδα: {nat_val})")
                
                
                if era_values:
                    content = (
                        f"Περιφέρεια: {region_name}\n"
                        f"Δείκτης: {ind}\n"
                        f"Περίοδος: {era_name}\n"
                        f"Δεδομένα: {', '.join(era_values)}"
                    )
                    
                    docs.append(Document(
                        page_content=content,
                        metadata={
                            "region": region_name,
                            "indicator": ind,
                            "era": era_name,
                            "source": sheet_label
                        }
                    ))
    
   
    return docs
