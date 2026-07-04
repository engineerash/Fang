import streamlit as st
import pandas as pd
from ioc_fanger import fang

st.title("IOC Fanger")

uploaded_file = st.file_uploader("Upload your IOC file", type=["xlsx", "csv"])

if uploaded_file:
    # Use pandas to read the file
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        # Take the first column and ensure they are strings
        raw_iocs = df.iloc[:, 0].dropna().astype(str).tolist()
        
        # Defang/Fang the IOCs
        cleaned_iocs = [fang(ioc) for ioc in raw_iocs]
        
        st.success("Successfully processed!")
        st.write("### Cleaned IOCs:")
        st.code("\n".join(cleaned_iocs))
        
    except Exception as e:
        st.error(f"Error processing file: {e}")
