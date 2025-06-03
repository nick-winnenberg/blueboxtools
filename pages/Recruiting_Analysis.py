import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt
import plotly.express as px



st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("Recruiting Analytics")
st.write("Goal: Quickly review an offices success via recruiting source.")
st.write("Tip: Export the Activity report as a CSV, drag it into the box, and go!")

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
    df = dfs[0]
    df = df.drop(df.index[:49])
    
    ind_for_drop = [0,1,3,4,7,9,10,11,12,13]
    col_for_drop = df.columns[ind_for_drop]
    df = df.drop(columns=col_for_drop)
    df = df.reset_index()

    index_to_drop = df[df.eq("Assignment Status").any(axis=1)].index

    if not index_to_drop.empty:
        df = df.iloc[:index_to_drop[0]]

    df = df.fillna(0)

    df.columns = df.iloc[0]

    df = df[1:].reset_index(drop=True)

    df = df.iloc[:, 1:]  # Keep all rows, drop the first column

    df["Applied"]=df["Applied"].astype(int)
    df["Eligible"]=df["Eligible"].astype(int)
    df["Assigned"]=df["Assigned"].astype(int)
    df["Source"]=df["Source"].astype(str)

    df["Placement Ratio"]=round(df["Assigned"]/df["Applied"]*100,2)
    df["Recruiting Power"] = df["Placement Ratio"] * df["Applied"]
    df["Recruiting Power Ratio"] = round(df["Recruiting Power"] / df["Recruiting Power"].sum() *100,2)
    df["Unassigned"]=df["Applied"]-df["Assigned"]

    df = df.sort_values(by="Recruiting Power",ascending=False)

    st.header("Recruiting Sources")
    st.write("Placement Ratio Assigned / Applied, suggesting how effective are we at using the sources.")
    st.write("Recruiting Power is a combination of the Placement Ratio and Applications.")
    st.dataframe(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Applications", df["Applied"].sum())
    col2.metric("Total Placements", df["Assigned"].sum())
    col3.metric("Placement Ratio (%)", round(df["Assigned"].sum()/df["Applied"].sum(),2)*100)

    st.subheader("Utilization of Applicants")

    df_sorted = df.sort_values(by="Applied", ascending=True)  # Sort by values


    df_melted = df_sorted.melt(id_vars=["Source"], value_vars=["Assigned", "Unassigned"], var_name="Category", value_name="Count")

    fig = px.bar(df_melted, x="Count", y="Source", color="Category", text="Count", orientation="h")

    st.plotly_chart(fig)

    st.subheader("Associates Applied")

    c = alt.Chart(df).mark_arc().encode(
        theta="Applied",
        color = "Source"
    )

    st.altair_chart(c)

    st.subheader("Associates Placed")

    c2 = alt.Chart(df).mark_arc().encode(
        theta="Assigned",
        color = "Source"
    )

    st.altair_chart(c2)



