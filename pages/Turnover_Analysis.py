import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt
import plotly.express as px


#Categorical Library
data = [
    ["Client canceled before start date", "Fired"],
    ["Associate canceled before start date", "Quit"],
    ["No show, no call (never reported)", "Quit"],
    ["Associate hired by client", "Good"],
    ["Associate could not extend", "Quit"],
    ["Associate ended assignment early", "Quit"],
    ["Associate hurt", "Other"],
    ["Associate terminated by Express", "Fired"],
    ["Associate walked off the job", "Quit"],
    ["Client dissatisfied with associate", "Fired"],
    ["Client transferred associate", "Good"],
    ["Client ended early (work load)", "Good"],
    ["Assignment completed", "Good"],
    ["No show, no call (after starting)", "Quit"]
]

# Create DataFrame
df_reason = pd.DataFrame(data, columns=["Assignment Status", "Category"])




st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("Turnover Analytics")
st.write("Goal: Quickly assess an offices turnover..")
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
    df = pd.concat(dfs, ignore_index=True)

## Selecting the specific area to analyze, using dynamic searching.
    starting_index = df[df.eq("Assignment Status").any(axis=1)].index 
    
    #Selecting only the desired turnover info
    if not starting_index.empty:
        df = df.iloc[starting_index[0]:] 
    df = df.drop(df.columns[[0,1,3,4,5,6,8,9,10,11,12,13]], axis=1)

    #Resetting the index to make it formated (titles, etc.)
    df = df.reset_index()
    df = df.drop(df.columns[[0]], axis=1)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    #Converting str to numbers for analytics
    df["Number"] = pd.to_numeric(df["Number"], errors="coerce").fillna(0).astype(int)
    df["Percentage"] = df["Number"] / df["Number"].sum() * 100

    #Adding in Analytics
    df["Percentage"] = df["Number"] / df["Number"].sum() * 100
    df = pd.merge(df, df_reason, on="Assignment Status", how="left")
    df_reason = df.groupby("Category", as_index=False).agg({
        "Number":"sum",
        "Percentage":"sum"
    }) 
    


    ### Visualizations

    #General Reasons for Turnover
    st.subheader("General Reasons for Turnover (%)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Good Turnover", round(df[df["Category"] == "Good"]["Percentage"].sum(),2))
    col2.metric("Fired", round(df[df["Category"] == "Fired"]["Percentage"].sum(),2))
    col3.metric("Quits", round(df[df["Category"] == "Quit"]["Percentage"].sum(),2))
    col4.metric("Other", round(df[df["Category"] == "Other"]["Percentage"].sum(),2))
    

    c = alt.Chart(df_reason).mark_arc().encode(
        theta="Percentage",
        color = "Category"
    )

    st.altair_chart(c)

    #Data Frame Visualizations
    st.subheader("Specific Reasons for Turnover")
    st.dataframe(df)


    #Turnover Chart and Header
    st.subheader("Specific Causes for Turnover")
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Number:Q", title="Number"),
        y=alt.Y("Assignment Status:N", sort="-x", title="Assignment Status"),
    ).configure_axis(
        labelAngle=0,
        labelFontSize=12,
        labelLimit=200
    )

    st.altair_chart(chart)



   


    
    