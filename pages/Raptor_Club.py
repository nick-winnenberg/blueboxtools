import pandas as pd
from datetime import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt

st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("Raptor Club")
st.write("Quickly sort the raptor club email, to see where your office lies in terms of top sales rep activities.")

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

    #Cleanup
    df = df.fillna(0)
    df = df.drop(df.index[:7])
    df = df.drop(df.columns[[12,13,14,15,16,17,18,19,20,21]], axis=1)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    df.rename(columns={0.0:'Rank',"New            Gross Margin":"New GM"},inplace=True)
    df['Outside Sales Hire Date'] = pd.to_datetime(df['Outside Sales Hire Date'], errors="coerce")
    df['Hire Date Year'] = df['Outside Sales Hire Date'].dt.year

    this_year = datetime.now().year
    this_week = datetime.now().isocalendar()[1]

    # Set Weeks Tracked only for rows hired this year
    df.loc[df['Hire Date Year'] == this_year, "Weeks Tracked"] = (
        this_week - df['Outside Sales Hire Date'].dt.isocalendar().week
    )
    df.loc[df['Hire Date Year'] < this_year, "Weeks Tracked"] = this_week

    df = df.fillna(0)
    df["Avg Sales Calls"] = round(df["Total Sales Calls"] / df["Weeks Tracked"],0)
    df["Avg DM Calls"] = round(df["Total DM Calls"] / df["Weeks Tracked"],0)
    df["Avg Apts"] = round(df["Total Appointments"] / df["Weeks Tracked"],0)
    df["Avg MPC Calls"] = round(df["Total MPC Calls"] / df["Weeks Tracked"],0)
    df["AVG GM Generated"] = round(df["New GM"] / df["Weeks Tracked"],0)
    df["AVG New Clients"] = round(df["New Clients Billed for Sales Rep"] / df["Weeks Tracked"],1)
    df["Projected GM"] =  df["AVG GM Generated"] * 52
    df["Projected Clients"] = df["AVG New Clients"] * 52

    df_weekly = df[["Rank","First Name","Last Name","Primary Office #","Developer","Zone","Avg Sales Calls","Avg DM Calls","Avg Apts","Avg MPC Calls","AVG GM Generated","AVG New Clients","Projected GM","Projected Clients"]]

    top25 = df_weekly[df_weekly["Rank"]<25]
    top50 = df_weekly[df_weekly["Rank"]<50]
    top100 = df_weekly[df_weekly["Rank"]<100]

    
    
    #st.subheader("Top 25 Metrics")
    #col1, col2, col3, col4 = st.columns(4)
    #col1.metric("DM Calls", round(top25["Avg DM Calls"].mean(),0) if df["Avg DM Calls"].count() > 0 else 0)
    #col2.metric("Apt Calls", round(top25["Avg Apts"].mean(),2) if df["Avg Apts"].count() > 0 else 0)
    #col3.metric("Clients per Week", round(top25["AVG New Clients"].mean(),2) if df["AVG New Clients"].count() > 0 else 0)
    #col4.metric("GM/Week", round(top25["AVG GM Generated"].mean(),0) if df["AVG GM Generated"].count() > 0 else 0)

    st.subheader("Top 50 Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("DM Calls", round(top50["Avg DM Calls"].mean(),0) if df["Avg DM Calls"].count() > 0 else 0)
    col2.metric("Apt Calls", round(top50["Avg Apts"].mean(),2) if df["Avg Apts"].count() > 0 else 0)
    col3.metric("Clients per Week", round(top50["AVG New Clients"].mean(),2) if df["AVG New Clients"].count() > 0 else 0)
    col4.metric("GM/Week", round(top50["AVG GM Generated"].mean(),0) if df["AVG GM Generated"].count() > 0 else 0)

    st.subheader("Top 100 Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("DM Calls", round(top100["Avg DM Calls"].mean(),0) if df["Avg DM Calls"].count() > 0 else 0)
    col2.metric("Apt Calls", round(top100["Avg Apts"].mean(),2) if df["Avg Apts"].count() > 0 else 0)
    col3.metric("Clients per Week", round(top100["AVG New Clients"].mean(),2) if df["AVG New Clients"].count() > 0 else 0)
    col4.metric("GM/Week", round(top100["AVG GM Generated"].mean(),0) if df["AVG GM Generated"].count() > 0 else 0)

    developer_list = sorted(df["Developer"].dropna().unique())
    zone_list = sorted(df["Zone"].dropna().unique())

    st.subheader("Developer Region")
    option = st.selectbox(
    "Who are you?",
    (developer_list),
    )

    st.write("You selected:", option)

    if option != None:
        developer_sr = df_weekly[df_weekly["Developer"]==option]
        developer_sr = developer_sr.drop(columns=["Developer"])

        group_cols = ["First Name", "Last Name"]  # or a combined "Sales Rep Name" column if you have one

        df_grouped = developer_sr.groupby(group_cols, as_index=False).agg({
            "Primary Office #": "first",  # assuming it's the same across duplicates
            "Avg Sales Calls": "sum",
            "Avg DM Calls": "sum",
            "Avg Apts": "sum",
            "Avg MPC Calls": "sum",
            "AVG GM Generated": "sum",
            "AVG New Clients": "sum",
            "Projected GM": "sum",
            "Projected Clients": "sum"
        })

        
        df_grouped
        st.text("Projected GM (Straight Line, I know, not ideal.)")
        c=(
        alt.Chart(df_grouped).mark_bar().encode(
            alt.X('Projected GM'),
            alt.Y('First Name',sort="-x")
            )
        )
    c

    st.subheader("Zone")
    option2 = st.selectbox(
    "Which Region?",
    (zone_list),
    )

    st.write("You selected:", option2)

    

    if option != None:
        zone_sr = df_weekly[df_weekly["Zone"]==option2]
        zone_sr = zone_sr.drop(columns=["Zone"])

        group_cols2 = ["First Name", "Last Name"]  # or a combined "Sales Rep Name" column if you have one

        df_grouped2 = zone_sr.groupby(group_cols2, as_index=False).agg({
            "Primary Office #": "first",  # assuming it's the same across duplicates
            "Avg Sales Calls": "sum",
            "Avg DM Calls": "sum",
            "Avg Apts": "sum",
            "Avg MPC Calls": "sum",
            "AVG GM Generated": "sum",
            "AVG New Clients": "sum",
            "Projected GM": "sum",
            "Projected Clients": "sum"
        })

        

        
        df_grouped2
        df_grouped2 = df_grouped2.fillna(0)

        df_grouped2["Avg DM Calls"] = df_grouped2["Avg DM Calls"].astype("float")
        df_grouped2["Avg Apts"] = df_grouped2["Avg Apts"].astype("float")
        df_grouped2["AVG New Clients"] = df_grouped2["AVG New Clients"].astype("float")
        df_grouped2["AVG GM Generated"] = df_grouped2["AVG GM Generated"].astype("float")


        st.subheader(option2)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("DM Calls", round(df_grouped2["Avg DM Calls"].mean(),0) if df["Avg DM Calls"].count() > 0 else 0)
        col2.metric("Apt Calls", round(df_grouped2["Avg Apts"].mean(),2) if df["Avg Apts"].count() > 0 else 0)
        col3.metric("Clients per Week", round(df_grouped2["AVG New Clients"].mean(),2) if df["AVG New Clients"].count() > 0 else 0)
        col4.metric("GM/Week", round(df_grouped2["AVG GM Generated"].mean(),0) if df["AVG GM Generated"].count() > 0 else 0)
        
        st.text("Projected GM (Straight Line, I know, not ideal.)")
        c=(
        alt.Chart(df_grouped2).mark_bar().encode(
            alt.X('Projected GM'),
            alt.Y('First Name',sort="-x")
            )
        )
    c

   