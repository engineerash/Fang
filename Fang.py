import streamlit as st
import pandas as pd
from ioc_fanger import fang

def classify_ioc(ioc):
    """Simple heuristic to label IOCs based on content."""
    ioc = ioc.lower()
    if any(x in ioc for x in ["http", "https", "://"]): return "url"
    if any(x in ioc for x in ["www", ".com", ".org", ".net"]): return "domain"
    # Basic IP detection
    if ioc.count('.') == 3 and all(p.isdigit() for p in ioc.split('.')): return "ip"
    # Hash detection based on length
    if len(ioc) == 32: return "md5"
    if len(ioc) == 40: return "sha1"
    if len(ioc) == 64: return "sha256"
    return "unknown"

def process_ioc_file(uploaded_file):
    """Processes uploaded file and returns a DataFrame with 'value,label' format."""
    # Reading file (adjust based on your specific Excel/CSV column names)
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    # Assume the first column contains the IOCs
    raw_iocs = df.iloc[:, 0].dropna().astype(str).tolist()
    
    processed_data = []
    for raw_ioc in raw_iocs:
        clean_ioc = fang(raw_ioc)
        label = classify_ioc(clean_ioc)
        processed_data.append({"value": clean_ioc, "label": label})
        
    return pd.DataFrame(processed_data)

st.title("SOC IOC to AQL Formatter")

uploaded_file = st.file_uploader("Upload your fanged IOC Excel/CSV", type=["xlsx", "csv"])

if uploaded_file:
    result_df = process_ioc_file(uploaded_file)
    st.write("### Processed IOCs (Ready for AQL Generator):")
    st.dataframe(result_df)
    
    # Convert to the CSV format your generator likely expects
    csv_data = result_df.to_csv(index=False)
    
    st.download_button(
        label="Download Formatted IOCs",
        data=csv_data,
        file_name="formatted_iocs.csv",
        mime="text/csv"
    )
