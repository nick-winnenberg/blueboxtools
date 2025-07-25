import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt
import plotly.express as px


st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("Touch to Close")
st.write("Goal: Use a HUGE call summary (seriously, export everything), to see how many touches it takes to land some of the major clients.")
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
    
    df = df[df["Date First Bill"].notnull()]
    df["dms"] = df["DM Reached"] == "Yes"
    df['Apt Flag'] = df['Call Type'] == 'Appointment call - face to face'
    df['Completed Date'] = pd.to_datetime(df['Completed Date'], errors="coerce")
    df['Date First Bill'] = pd.to_datetime(df['Date First Bill'], errors="coerce")

    df_precall = df[df["Completed Date"]<df["Date First Bill"]]

    touches_before = df_precall.groupby("Company Name").agg(
        All_Calls=("Results",'size'),
        DM_Calls=("dms","sum"),
        Apt_Calls=("Apt Flag","sum")).sort_values(
            by=['All_Calls'], ascending=False).reset_index()
    
    st.subheader("Average Touches to Land")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average All Calls", round(touches_before["All_Calls"].mean(),2),help="Number Of Companies Contacted")
    col2.metric("Average DM Calls", round(touches_before["DM_Calls"].mean(),2),help="Number Of Companies with atleast one DM connection.")
    col3.metric("Average Apt Calls", round(touches_before["Apt_Calls"].mean(),2),help="Number Of Companies with atleast one appointment.")

    st.subheader("Per Client")
    touches_before



    
    



        


        


        
        










