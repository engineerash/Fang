import streamlit as st
import pandas as pd
from ioc_fanger import fang

def classify_ioc(ioc):
    """Categorizes the indicator type for AQL mapping."""
    ioc = ioc.lower()
    if any(x in ioc for x in ["http", "https", "://"]): return "url"
    if any(x in ioc for x in ["www", ".com", ".org", ".net"]): return "domain"
    if ioc.count('.') == 3 and all(p.isdigit() for p in ioc.split('.')): return "ip"
    if len(ioc) == 32: return "md5"
    if len(ioc) == 40: return "sha1"
    if len(ioc) == 64: return "sha256"
    return "filename"

st.title("🛡️ SOC IOC Defanger & Sorter")

uploaded_file = st.file_uploader("Upload your fanged IOC Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    # 1. Load Data
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    # 2. Defang and Sort
    # Assumes the first column contains the raw indicators
    raw_iocs = df.iloc[:, 0].dropna().astype(str).tolist()
    
    processed_data = []
    for item in raw_iocs:
        clean_ioc = fang(item)
        category = classify_ioc(clean_ioc)
        processed_data.append({"value": clean_ioc, "type": category})
    
    # Create DataFrame for display
    results_df = pd.DataFrame(processed_data).drop_duplicates()
    
    # 3. Sort by type to keep the text file clean
    results_df = results_df.sort_values(by="type")
    
    st.write("### Processed & Sorted IOCs")
    st.dataframe(results_df)
    
    # 4. Prepare TXT output (formatted as value,label for your AQL generator)
    txt_output = "\n".join([f"{row['value']},{row['type']}" for _, row in results_df.iterrows()])
    
    st.download_button(
        label="Download Formatted IOCs (.txt)",
        data=txt_output,
        file_name="processed_iocs.txt",
        mime="text/plain"
    )
