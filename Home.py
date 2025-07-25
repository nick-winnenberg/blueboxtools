import pandas as pd
import datetime
import numpy as np
import os
import streamlit as st
from pathlib import Path
import altair as alt

st.sidebar.success("☝️ Check out these bluebox tools.☝️")

st.header("Welcome to Bluebox Developer Tools!")
st.text("This is an updated directory, using cloud tools, to automate some developer reponsibilities. This code is maintained by Nick Winnenberg. Please email me or send me a teams message with any questions.")

st.markdown("**Updates V 0.15**")
st.markdown("- Added multi-sheet functionality to combine offices/sales reps into a single dataframe. AKA, you can upload multiple sheets at the same time.")
st.markdown("- Added Turnover and Recruiting Analysis tools that utilize an exported activity report.")

st.markdown("##")

st.subheader("Activity Report Tools",divider=True)
st.text("All you need to do is export the activity report, then upload it into the tool. Magic!")
st.subheader("Recruiting Analysis ❗")
st.text("Use an exported activity report to understand the recruiting themes in an office.")
st.subheader("Turnover Analysis 🎭")
st.text("Use an exported activity report to understand the turnover themes in an office.")

st.markdown("##")

st.subheader("Client Prospect Activity Detail Tools",divider=True)
st.text("Exporting is tricky! Make sure you go to My Menu -> Preferences -> Sales Planner -> Client Prospect Activity Details filtered by Completed Date -> Move all the Columns Available to the Columns Chosen. Export, then drag and drop! Call me on Teams if you need help with this.")
st.subheader("Client Pipeline 💸")
st.text("Use an exported call summary to see which companies are being called on, and the health of their pipeline (DM Connections, Appointments, etc.) It's a quick and easy way to have a conversation about a sales representatives current funnel")
st.subheader("Sales Coach 🤓")
st.text("Use an exported call summary to analyze the overall success of a sales representative, or an office, with a few additional sales metrics thrown into the game. Great high level overview.")
st.subheader("Sales Rep Weekly Calls Report Card 🔎")
st.text("Use an exported call summary, over multiple weeks, to analyze trends in sales rep activities, and give you an easy to read report card on their progress, against the Express Power Plays.")
st.subheader("Multi User Client Report🏦")
st.text("Use an exported call summary, to analyze who all is calling on individual companies. Thanks Kris, Tony, and Brian!")
st.subheader("MPC Report")
st.text("Use an exported call summary, to analyze who is having MPC connections in an office!")
st.subheader("Touch to Close")
st.text("Use a HUGE call summary (seriously, export EVERYTHING, to see how many touches it takes to land some of the major clients. Thanks Cherri!")

st.markdown("##")

st.subheader("Other Reports",divider=True)
st.subheader("Raptor Club 🦅")
st.text("Use the Weekly Raptor Club Email to see where your sales reps compare to the weekly averages of the top-50 and top-100.")

