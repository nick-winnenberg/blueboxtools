import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt




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

months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# Create DataFrame
df_reason = pd.DataFrame(data, columns=["Reason", "Category"])

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

    df_stat_block = df
    turnover_reasons = df
    df_season = df
    df_job = df

    #Creating the Stat Block
    df_stat_block = df_stat_block.drop(df_stat_block.columns[[0,1,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18,19,20,21,22,23]], axis=1)

    starting_index = df_stat_block[df_stat_block.eq("People ordered for temporary assignment").any(axis=1)].index
    if not starting_index.empty:
        df_stat_block = df_stat_block.iloc[starting_index[0]:]
    
    df_stat_block=df_stat_block.reset_index()

    ending_index = df_stat_block[df_stat_block.eq("Ordering Trends").any(axis=1)].index
    if not ending_index.empty:
        df_stat_block = df_stat_block.iloc[:ending_index[0]]

    
    df_stat_block = df_stat_block.drop(df_stat_block.columns[[0]], axis=1)

    #Creating the Reasons for Turnover (and categories)
    turnover_reasons = turnover_reasons.drop(turnover_reasons.columns[[0,1,2,3,4,5,7,8,9,10,11,12,13,14,16,17,18,19,20,21,22,23]], axis=1)

    starting_index_2 = turnover_reasons[turnover_reasons.eq("Assignment completed").any(axis=1)].index
    if not starting_index_2.empty:
        turnover_reasons = turnover_reasons.iloc[starting_index_2[0]:]
    
    turnover_reasons=turnover_reasons.reset_index()

    ending_index_2 = turnover_reasons[turnover_reasons.eq("No show, no call (never reported)").any(axis=1)].index
    if not ending_index_2.empty:
        turnover_reasons = turnover_reasons.iloc[:ending_index_2[0]]

    turnover_reasons = turnover_reasons.drop(turnover_reasons.columns[[0]], axis=1)

    turnover_reasons.rename(columns={"Unnamed: 6":'Reason',"Unnamed: 15":"Number"},inplace=True)

    turnover_reasons["Number"] = pd.to_numeric(turnover_reasons["Number"], errors="coerce").fillna(0).astype(int)
    turnover_reasons["Percentage"] = turnover_reasons["Number"] / turnover_reasons["Number"].sum() * 100

    turnover_reasons = pd.merge(turnover_reasons, df_reason, on="Reason", how="left")
    turnover_reasons_cat = turnover_reasons.groupby("Category", as_index=False).agg({
        "Number":"sum",
        "Percentage":"sum"
    }) 

    ## Creating the Seasonality

    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    df_season = df.drop(df.columns[[0,1,2,3,4,5,7,8,9,10,11,13,14,15,16,17,18,19,20,21,22,23]], axis=1)

    # Search for any cell that matches a month name
    match_indices = df_season.apply(lambda row: row.astype(str).str.contains('|'.join(months))).any(axis=1)
    start_idx = match_indices[match_indices].index[0]
    df_season= df_season.iloc[start_idx:].reset_index(drop=True)

    ending_idx = df_season[df_season.eq("Express").any(axis=1)].index
    if not ending_idx.empty:
        df_season = df_season.iloc[:ending_idx[0]]

    df_season.rename(columns={"Unnamed: 6":'Season',"Unnamed: 12":"Number"},inplace=True)

    ## Creating Job Breakdown

    starting_index_3 = df_job[df_job.eq("By Job Title").any(axis=1)].index
    if not starting_index_3.empty:
        df_job = df_job.iloc[starting_index_3[0]:]
    
    df_job=df_job.reset_index()

    ending_index_3 = df_job[df_job.eq("By Month").any(axis=1)].index
    if not ending_index_3.empty:
        df_job = df_job.iloc[:ending_index_3[0]]
  
    df_job = df_job.drop(df_job.columns[[0,1,2,3,4,5,6,8,9,10,11,12,14,15,16,17,18,19,20,21,22,23,24]], axis=1)

    df_job.rename(columns={"Unnamed: 6":'Job',"Unnamed: 12":"Number"},inplace=True)

    ### Visualizations
    st.subheader("Staffing Ratios")

    assigned_row = df[df.eq("Express").any(axis=1)].index

    col1, col2, col3= st.columns(3)
    col1.metric("Associates Requested",df_stat_block.loc[df_stat_block['Unnamed: 2'] == 'People ordered for temporary assignment', 'Unnamed: 16'].values[0])
    col2.metric("Associates Assigned",df.loc[df['Unnamed: 7'] == 'Express', 'Unnamed: 12'].values[0])
    col3.metric("Assignment Completed",turnover_reasons["Number"].sum())


 

    ## Hiring Timelines
    st.subheader("Hiring Timelines")

    month_order = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]

    df_season['Season'] = pd.Categorical(df_season['Season'], categories=month_order, ordered=True)

    
    fig, ax = plt.subplots(figsize=(10, 5))  # Optional: adjust size
    
    sns.barplot(data=df_season, x='Season', y='Number')




    # Customize the plot (optional)
    ax.set_title("Seasonality")
    ax.set_ylabel("Assignments")
    ax.set_xlabel("Month")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Show it in Streamlit
    st.pyplot(fig)
    st.write("Keep in mind, that this is could be across multiple years, showcasing when the majority of the hiring is done, based on the month.")

        ## By Position
    st.subheader("By Position")
    c1 = (
        alt.Chart(df_job).mark_bar().encode(
            alt.X('Number:Q', sort='-y'),  # Quantitative axis
            alt.Y('Job:N', sort='-x').axis(labelLimit=0)      # Nominal axis
        )
    )
    c1


    #General Reasons for Turnover
    st.subheader("General Reasons for Turnover (%)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Good Turnover", round(turnover_reasons[turnover_reasons["Category"] == "Good"]["Percentage"].sum(),2))
    col2.metric("Fired", round(turnover_reasons[turnover_reasons["Category"] == "Fired"]["Percentage"].sum(),2))
    col3.metric("Quits", round(turnover_reasons[turnover_reasons["Category"] == "Quit"]["Percentage"].sum(),2))
    col4.metric("Other", round(turnover_reasons[turnover_reasons["Category"] == "Other"]["Percentage"].sum(),2))
    

    c = alt.Chart(turnover_reasons_cat).mark_arc().encode(
        theta="Percentage",
        color = "Category"
    )

    st.altair_chart(c)

    #Data Frame Visualizations
    st.subheader("Specific Reasons for Turnover")
    st.dataframe(turnover_reasons)






   


    
    