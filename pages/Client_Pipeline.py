import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt


st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("Client Pipeline")
st.write("Goal: Quick Dashboard of all of the clients and office is prospecting, including activity call types.")
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

#Real Code
if len(dfs)>0:
    df = dfs[0]
    company_pipeline = df[["Company Name","Completed Date","Call Type","Results"]]
    
    df['Discovery Flag'] = df['Call Type'].apply(lambda x: 1 if 'Discovery call - face to face' else 0)
    df["dms"] = df["DM Reached"] == "Yes"
    df['Apt Flag'] = df['Call Type'] == 'Appointment call - face to face'
    df['Client Flag'] = df["Date First Bill"].notna()
    
    
    clients = df.groupby("Company Name").agg(All_Calls=("Results",'size'),DM_Calls=("dms","sum"),Appointment_Calls=("Apt Flag","sum"),Billed_Before=("Client Flag","mean")).sort_values(by=['All_Calls'], ascending=False)
    clients["Billed_Before"] = clients["Billed_Before"] == 1

    st.dataframe(clients)

        


        
        










