import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt


st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("Multi User Client Report")
st.write("Goal: See who all in the office is calling on certain companies.")
st.write("Tip: Make sure you edit your call summary dashboard to include all the possible fields in the client prospect activity detail. Export the file, and then drag and drop into the tool!")

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
    df = pd.concat(dfs, ignore_index=True)
    user_list = sorted(df["Completed By"].dropna().unique())

    call_matrix = df.pivot_table(
        index='Company Name',
        columns='Completed By',
        aggfunc='size',
        fill_value=0
    )

    call_matrix['User Count'] = (call_matrix > 0).sum(axis=1)
    cols = ['User Count'] + [col for col in call_matrix.columns if col != 'User Count']
    call_matrix = call_matrix[cols]

    call_matrix = call_matrix.sort_values(by="User Count", ascending=False)

    st.subheader("All Calls by Client and User")
    st.dataframe(call_matrix)




        


        


        
        










