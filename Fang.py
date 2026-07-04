import streamlit as st
import pandas as pd
from ioc_fanger import fang

# Page configuration
st.set_page_config(page_title="SOC IOC Defanger", page_icon="🛡️")

def classify_ioc(ioc):
    """Categorizes the indicator type for AQL mapping."""
    ioc = ioc.lower()
    if any(x in ioc for x in ["http", "https", "://"]): return "url"
    if any(x in ioc for x in ["www", ".com", ".org", ".net"]): return "domain"
    # Basic IP detection
    if ioc.count('.') == 3 and all(p.isdigit() for p in ioc.split('.')): return "ip"
    # Hash detection based on length
    if len(ioc) == 32: return "md5"
    if len(ioc) == 40: return "sha1"
    if len(ioc) == 64: return "sha256"
    return "filename"

st.title("🛡️ SOC IOC Defanger & Sorter")
st.markdown("Upload your Excel/CSV file to defang and categorize IOCs for your AQL generator.")

uploaded_file = st.file_uploader("Upload fanged IOC file", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Load Data: header=None treats the first row as data, not column headers
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, header=None)
        else:
            df = pd.read_csv(uploaded_file, header=None)
        
        # Select first column and drop empty cells
        raw_iocs = df.iloc[:, 0].dropna().astype(str).tolist()
        
        # Defang and Sort
        processed_data = []
        for item in raw_iocs:
            clean_ioc = fang(item)
            category = classify_ioc(clean_ioc)
            processed_data.append({"value": clean_ioc, "type": category})
        
        # Create DataFrame and sort
        results_df = pd.DataFrame(processed_data).drop_duplicates()
        results_df = results_df.sort_values(by="type")
        
        st.write("### Processed & Sorted IOCs")
        st.dataframe(results_df)
        
        # Prepare TXT output (formatted as value,label)
        txt_output = "\n".join([f"{row['value']},{row['type']}" for _, row in results_df.iterrows()])
        
        st.download_button(
            label="Download Formatted IOCs (.txt)",
            data=txt_output,
            file_name="processed_iocs.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Error processing file: {e}")
