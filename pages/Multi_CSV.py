import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt


st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("Multi CSV Combiner")
st.write("Combine multiple CSV files into one master CSV file. You can upload multiple CSVs, and the tool will combine them while keeping the columns from the first CSV. You can then download the combined master CSV file.")

files_dict = {}

# Streamlit file uploader
uploaded_files = st.file_uploader("Upload your files", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        filename = Path(uploaded_file.name).stem  # Get filename without extension
        
        try:
            # Load file based on extension
            if uploaded_file.name.endswith('.csv'):
                files_dict[filename] = pd.read_csv(uploaded_file, encoding='cp1252')
            elif uploaded_file.name.endswith(('.xls', '.xlsx')):
                files_dict[filename] = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.txt'):
                files_dict[filename] = pd.read_csv(uploaded_file, delimiter='\t', encoding='cp1252')
            elif uploaded_file.name.endswith('.json'):
                files_dict[filename] = pd.read_json(uploaded_file)
            else:
                st.warning(f"Unsupported file type for {uploaded_file.name}")
                continue
                
            st.success(f"Successfully loaded: {filename}")
            
        except Exception as e:
            st.error(f"Error loading {filename}: {str(e)}")

# Display the loaded dataframes
dfs = []
for name, df in files_dict.items():
    dfs.append(df)

if len(dfs)>0:
    # Combine all CSVs into one master dataframe, keeping the first CSV's columns
    master_df = pd.concat(dfs, ignore_index=True)
    
    st.write("### Master CSV Preview")
    st.dataframe(master_df)
    
    # Download button for master CSV
    csv_output = master_df.to_csv(index=False, encoding='cp1252')
    st.download_button(
        label="Download Master CSV",
        data=csv_output,
        file_name="master_combined.csv",
        mime="text/csv"
    )


    




        


        


        
        










