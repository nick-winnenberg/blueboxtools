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

#Categorical Library
r_data = [
["AARP","Physical"],
["Bulletin Board Posting","Physical"],
["Classified Ad - Online","Search"],
["Classified Ad - Print","Physical"],
["Direct Recruit","Direct"],
["Drive-By/Signage/Billboard","Physical"],
["EBS","Physical"],
["Emsi","Job Board"],
["Existing Client","WOM"],
["Express Representative","Direct"],
["Pandologic","Job Board"],
["Publication/Article","Physical"],
["Radio","Physical"],
["Referral - Business/Organization","WOM"],
["Referral - Individual","WOM"],
["Returning Applicant","WOM"],
["Search Engine - Bing","Search"],
["Search Engine - Google","Search"],
["Search Engine - Other","Search"],
["Search Engine - Yahoo","Search"],
["Social Media - Facebook","Search"],
["Social Media - Instagram","Social"],
["Social Media - LinkedIn","Social"],
["Social Media - Other","Social"],
["Social Media - Snapchat","Social"],
["Social Media - Twitter","Social"],
["Television","Physical"],
["TextRecruit","Direct"],
["Trade Show/Job Fair","Direct"],
["Web Job Boards - CareerBuilder","Job Board"],
["Web Job Boards - craigslist","Job Board"],
["Web Job Boards - Indeed","Job Board"],
["Web Job Boards - LinkedIn Slot","Job Board"],
["Web Job Boards - Monster","Job Board"],
["Web Job Boards - Other","Job Board"],
["Web Job Boards - Snagajob","Job Board"],
["www.expresspros.com","Search"],
["Yellow Pages Ad","Search"],
["ZipRecruiter","Job Board"]
]

df_source = pd.DataFrame(r_data, columns=["Source", "Source Category"])

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

    df = pd.merge(df, df_source, on="Source", how="left")

    df["Applied"] = pd.to_numeric(df["Applied"].str.replace(",", ""), errors="coerce").fillna(0).astype(int)
    df["Eligible"] = pd.to_numeric(df["Eligible"].str.replace(",", ""), errors="coerce").fillna(0).astype(int)
    df["Assigned"] = pd.to_numeric(df["Assigned"].str.replace(",", ""), errors="coerce").fillna(0).astype(int)
    df["Source"]=df["Source"].astype(str)

    df["Placement Ratio"]=round(df["Assigned"]/df["Applied"]*100,2)
    df["Recruiting Power"] = df["Placement Ratio"] * df["Applied"]
    df["Recruiting Power Ratio"] = round(df["Recruiting Power"] / df["Recruiting Power"].sum() *100,2)
    df["Unassigned"]=df["Applied"]-df["Assigned"]

    df = df.sort_values(by="Recruiting Power",ascending=False)

    ## Creating a category based DF 
    df_category = df.groupby("Source Category", as_index=False).agg({
        "Applied":"sum",
        "Eligible":"sum",
        "Assigned":"sum",
    }) 

    df_category["Placement Ratio"] = round(df_category["Assigned"]/df_category["Applied"]*100,2)
    df_category["Percent of Total Applications"] = round(df_category["Applied"]/df_category["Applied"].sum()*100,2)
    df_category["Percent of Total Placements"] = round(df_category["Assigned"]/df_category["Assigned"].sum()*100,2)

    ## Visualizations
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

    st.header("Categories")
    st.subheader("Associates Applied (%) of Total Applications")

    col1, col2, col3= st.columns(3)
    col1.metric("Word of Mouth", round(df_category[df_category["Source Category"] == "WOM"]["Percent of Total Applications"].sum(),2))
    col2.metric("Job Boards", round(df_category[df_category["Source Category"] == "Job Board"]["Percent of Total Applications"].sum(),2))
    col3.metric("Social", round(df_category[df_category["Source Category"] == "Social"]["Percent of Total Applications"].sum(),2))

    col4, col5, col6= st.columns(3)
    col4.metric("Direct", round(df_category[df_category["Source Category"] == "Direct"]["Percent of Total Applications"].sum(),2))
    col5.metric("Physical", round(df_category[df_category["Source Category"] == "Physical"]["Percent of Total Applications"].sum(),2))
    col6.metric("Search", round(df_category[df_category["Source Category"] == "Search"]["Percent of Total Applications"].sum(),2))
    

    c = alt.Chart(df_category).mark_arc().encode(
        theta="Applied",
        color = "Source Category"
    )

    st.altair_chart(c)

    st.subheader("Associates Placed (%) of Total Placements")
    col1, col2, col3= st.columns(3)
    col1.metric("Word of Mouth", round(df_category[df_category["Source Category"] == "WOM"]["Percent of Total Placements"].sum(),2))
    col2.metric("Job Boards", round(df_category[df_category["Source Category"] == "Job Board"]["Percent of Total Placements"].sum(),2))
    col3.metric("Social", round(df_category[df_category["Source Category"] == "Social"]["Percent of Total Placements"].sum(),2))

    col4, col5, col6= st.columns(3)
    col4.metric("Direct", round(df_category[df_category["Source Category"] == "Direct"]["Percent of Total Placements"].sum(),2))
    col5.metric("Physical", round(df_category[df_category["Source Category"] == "Physical"]["Percent of Total Placements"].sum(),2))
    col6.metric("Search", round(df_category[df_category["Source Category"] == "Search"]["Percent of Total Placements"].sum(),2))

    c2 = alt.Chart(df_category).mark_arc().encode(
        theta="Assigned",
        color = "Source Category"
    )

    st.altair_chart(c2)


