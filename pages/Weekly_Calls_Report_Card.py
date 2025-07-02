import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt

st.sidebar.success("☝️ Check out these bluebox tools.☝️")
st.header("Weekly Activities")
st.write("Goal: Give you a general trend on how the sales rep is doing, completing certain activities.")
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
    df['Completed Date'] = pd.to_datetime(df['Completed Date'], errors="coerce")
    df["iso week"] = df["Completed Date"].dt.isocalendar().week
    df['Year Billed'] = df ['Completed Date'].dt.year
    df["Date Code"] = df['Year Billed'].astype(str) + df['iso week'].astype(str)
    df['Discovery Flag'] = df['Call Type'].apply(lambda x: 1 if 'Discovery call - face to face' else 0)
    df["dms"] = df["DM Reached"] == "Yes"
    df['Apt Flag'] = df['Call Type'] == 'Appointment call - face to face'
    df['Client Flag'] = df["Date First Bill"].notna()

    weekly = df.groupby("Date Code").agg(
        Week=("iso week","mean"),
        Completed_Date=("Completed Date","mean"),
        All_Calls=("Results",'size'),
        DM_Calls=("dms","sum"),
        Appointment_Calls=("Apt Flag","sum")
        ).sort_values(by=['Completed_Date'], ascending=True)
    weekly = weekly.reset_index()
    weekly.insert(0,"Tracked Week", range(1,1+len(weekly)))

    company_contacts = df.groupby("Company Name").agg(All_Calls=("Results",'size'),Clients=("Client Flag",'mean')).sort_values(by=['All_Calls'], ascending=False)
    
    user = df.groupby("Completed By").agg(
        All_Calls=("Results",'size'),
        DM_Calls=("dms","sum"),
        APT_Calls=("Apt Flag","sum"),
        Client_Ratio = ("Client Flag","mean")
        ).sort_values(by=['All_Calls'], ascending=False)
    user["Percent of calls"]=round(user["All_Calls"]/sum(user["All_Calls"])*100,2)
    user = user.reset_index()

    week_count = len(weekly)
    dm_count = (df["dms"] == True).sum()
    apt_count = (df["Apt Flag"] == True).sum()
    companies = (df["Company Name"]).nunique()
    single_contact_companies = (company_contacts["All_Calls"]==1).sum()
    active_client_count = (company_contacts["Clients"]==1).sum()

    st.subheader("Report Card")
    col1, col2, col3 = st.columns(3)
    col1.metric("Weeks",week_count)
    col2.metric("All Calls",len(df))
    col3.metric("Unique Companies",companies)

    all_weekly = "Mid"
    dm_weekly = "Mid"
    apt_weekly = "Mid"

    if len(df)/week_count > 100:
        all_weekly = "High"
    elif len(df)/week_count< 60:
        all_weekly = "Low"

    if dm_count/week_count > 60:
        dm_weekly = "High"
    elif dm_count/week_count< 30:
        dm_weekly = "Low"

    if apt_count/week_count > 7:
        apt_weekly = "High"
    elif apt_count/week_count< 3:
        apt_weekly = "Low"

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Weekly Calls", round(len(df) / week_count), delta=all_weekly, delta_color="off")
    col2.metric("AVG DM Calls", round(dm_count / week_count), delta=dm_weekly, delta_color="off")
    col3.metric("AVG Appointment Calls", round(apt_count / week_count), delta=apt_weekly, delta_color="off")


    ratio_dm = "Mid"
    ratio_fu = "Mid"
    prospect = "Mid"

    if dm_count/len(df) > .60:
        ratio_dm = "High"
    elif dm_count/len(df)< .30:
        ratio_dm = "Low"

    if 1-round(single_contact_companies/companies,2) > .75:
        ratio_fu = "High"
    elif 1-round(single_contact_companies/companies,2)< .70:
        ratio_fu = "Low"

    if (companies-active_client_count)/companies > .7:
        prospect = "High"
    elif (companies-active_client_count)/companies < .5:
        prospect = "Low"

    col1, col2, col3 = st.columns(3)
    col1.metric("DM Ratio",round(dm_count/len(df),2),delta=ratio_dm,delta_color="off")
    col2.metric("Follow Up Ratio",round(1-(single_contact_companies/companies),2),delta=ratio_fu,delta_color="off")
    col3.metric("Prospect/Client Ratio", round((companies-active_client_count)/companies,2),delta=prospect,delta_color="off")
    
    st.subheader("All Calls and DM Calls")
    st.area_chart(weekly,x="Tracked Week",y=["All_Calls","DM_Calls"])

    st.subheader("Appointment Calls")
    st.bar_chart(weekly, x="Tracked Week", y="Appointment_Calls")

    #st.subheader("Weekly Calls Table")
    #st.dataframe(weekly)


    st.subheader("Appointments")
    apts = df[df["Call Type"]== "Appointment call - face to face"]
    apts = apts[["Completed Date","Company Name","Results"]]
    #apts = apts.drop(columns=["Completed Date","Date First Bill","Territory","Last Contacted","Phone","Date Last Bill","Call Type","Grade","Day Completed","Year Billed","Never Billed","Apt Set","MPC","DM Count","Apt Count"])
    st.dataframe(apts)

    st.subheader("User Scoreboard")
    st.dataframe(user)

    st.subheader("All Calls")
    c=(
        alt.Chart(user).mark_bar().encode(
            alt.X('All_Calls'),
            alt.Y('Completed By',sort="-x")
            )
        )
    c





 