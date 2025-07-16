import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt


st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("MPC Report")
st.write("Track who is completing MPC Calls in an office")
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

    df["MPC"] = df["Results"].str.contains("MPC", case="False",na=False)
    df['Completed Date'] = pd.to_datetime(df['Completed Date'], errors="coerce")
    df["Week"] =df["Completed Date"].dt.isocalendar().week

    pivot_table = df.pivot_table(
    index='Week',
    columns='Completed By',
    values='MPC',
    aggfunc='sum',
    fill_value=0
    )

    pivot_table['Total'] = pivot_table.sum(axis=1)


    st.subheader("Office Scoreboard")
    pivot_table

    st.subheader("Total MPC's per Week")

    weekly_mpc_total = df.groupby("Week")["MPC"].sum().reset_index()
  
    st.bar_chart(weekly_mpc_total,x="Week",y="MPC")

    st.subheader("Employee Audit")
    option = st.selectbox(
        "Which User?",
        (user_list)
    )

    if option != None:
        user = option

        df2 = df[(df["Completed By"] == user) & (df["MPC"] == True)]

        df2




    




        


        


        
        










