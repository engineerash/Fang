import streamlit as st
import pandas as pd
from ioc_fanger import fang

st.set_page_config(page_title="SOC IOC Parser", page_icon="🛡️")

st.title("🛡️ SOC Dynamic IOC Parser")

# Function to dynamically map labels to your required AQL fields
def get_standard_label(raw_label):
    label = str(raw_label).lower().replace("_", " ").strip()
    
    # Mapping logic: If it contains a keyword, map to target standard
    if any(x in label for x in ["md5"]): return "MD5"
    if any(x in label for x in ["sha1"]): return "SHA1"
    if any(x in label for x in ["sha256"]): return "SHA256"
    if any(x in label for x in ["sender", "from"]): return "SENDER"
    if any(x in label for x in ["subject", "title"]): return "SUBJECT"
    if any(x in label for x in ["file path", "path"]): return "PATH" # Mapping 'file path' to 'PATH'
    if any(x in label for x in ["file"]): return "FILE"
    if any(x in label for x in ["ip", "address"]): return "IP Address"
    if any(x in label for x in ["fqdn", "domain"]): return "FQDN"
    if any(x in label for x in ["url", "link"]): return "URL"
    return "OTHER"

uploaded_file = st.file_uploader("Upload your IOC file", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Load Data
        df = pd.read_excel(uploaded_file, header=None) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file, header=None)
        
        processed_data = []
        for _, row in df.iterrows():
            raw_type = row[0] 
            raw_value = row[1]
            
            if pd.notna(raw_value) and str(raw_value).lower() != 'nan':
                # Dynamically map and defang
                clean_type = get_standard_label(raw_type)
                clean_value = fang(str(raw_value))
                
                processed_data.append({"value": clean_value, "type": clean_type})
        
        results_df = pd.DataFrame(processed_data).drop_duplicates()
        
        st.write("### Processed & Sorted IOCs")
        st.dataframe(results_df)
        
        txt_output = "\n".join([f"{row['value']},{row['type']}" for _, row in results_df.iterrows()])
        
        st.download_button("Download Formatted IOCs (.txt)", txt_output, "processed_iocs.txt", "text/plain")
        
    except Exception as e:
        st.error(f"Error processing file: {e}")
