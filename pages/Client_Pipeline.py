import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt


st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("Client Pipeline")
st.write("Goal: Quickly audit an office or sales reps calls, to determine validity (helpful for contests). Also create Quick Dashboard of all of the clients and office is prospecting, including activity call types.")
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

    company_pipeline = df[["Company Name","Completed Date","Call Type","Results"]]
    
    df['Discovery Flag'] = df['Call Type'].apply(lambda x: 1 if 'Discovery call - face to face' else 0)
    df["dms"] = df["DM Reached"] == "Yes"
    df['Apt Flag'] = df['Call Type'] == 'Appointment call - face to face'
    df['Client Flag'] = df["Date First Bill"].notna()
    df["Apt Set"] = df["Results"].str.contains("Appointment Set", case="False",na=False)
    
    clients = df.groupby("Company Name").agg(All_Calls=("Results",'size'),DM_Calls=("dms","sum"),Apt_Calls=("Apt Flag","sum"),Billed_Before=("Client Flag","mean")).sort_values(by=['All_Calls'], ascending=False)
    clients["Billed_Before"] = clients["Billed_Before"] == 1
    clients["Call Percent (%)"] = round(clients["All_Calls"] / clients["All_Calls"].sum()*100,2)

    st.header("Prospect Pipeline")
    col1, col2, col3 = st.columns(3)
    col1.metric("Leads", len(clients),help="Number Of Companies Contacted")
    col2.metric("Courting", len(clients[clients["DM_Calls"] >0]),help="Number Of Companies with atleast one DM connection.")
    col3.metric("Closing", len(clients[clients["Apt_Calls"] >0]),help="Number Of Companies with atleast one appointment.")

    st.subheader("Company Contacts")
    st.dataframe(clients)

    apt_set_audit = df[df["Apt Flag"]].sort_values("Company Name")
    st.subheader("Appointments")
    st.dataframe(apt_set_audit)



        


        


        
        










