import streamlit as st
import pandas as pd
from ioc_fanger import fang

st.set_page_config(page_title="SOC IOC Parser", page_icon="🛡️")

st.title("🛡️ SOC Key-Value IOC Parser")

uploaded_file = st.file_uploader("Upload your IOC file", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Load Data
        df = pd.read_excel(uploaded_file, header=None) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file, header=None)
        
        processed_data = []
        
        # Iterate through each row
        for _, row in df.iterrows():
            ioc_type = str(row[0]) # Column A: The label (e.g., "Mail Sender")
            ioc_value = str(row[1]) # Column B: The actual indicator
            
            if pd.notna(ioc_value) and ioc_value.lower() != 'nan':
                # Defang the value
                clean_val = fang(ioc_value)
                
                # Sanitize the type label for the AQL generator
                # e.g., "Mail Sender" -> "mail_sender"
                clean_type = ioc_type.lower().replace(" ", "_")
                
                processed_data.append({"value": clean_val, "type": clean_type})
        
        results_df = pd.DataFrame(processed_data).drop_duplicates()
        
        st.write("### Processed & Sorted IOCs")
        st.dataframe(results_df)
        
        # Prepare for your AQL generator
        txt_output = "\n".join([f"{row['value']},{row['type']}" for _, row in results_df.iterrows()])
        
        st.download_button("Download Formatted IOCs (.txt)", txt_output, "processed_iocs.txt", "text/plain")
        
    except Exception as e:
        st.error(f"Error processing file: {e}")
