
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
crm = pd.read_csv("Cleaned_CRM_Appointments_Merged.csv")
google_ads = pd.read_csv("Google_Ads.csv")
meta_ads = pd.read_csv("Cleaned_Meta_Ads.csv")
clusters = pd.read_csv("Clustered_Leads.csv")
churn = pd.read_csv("Churn_Summary_Insights.csv")

st.set_page_config(page_title="Auto Resale Dashboard", layout="wide")
st.title("Auto Resale Marketing & Sales Dashboard")

# Overview KPIs
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Leads", len(crm))
col2.metric("Total Sold", crm['Lead Status Type'].eq('Sold').sum())
col3.metric("Total Google + Meta Spend", 
            f"${google_ads['Cost'].sum() + meta_ads['Amount spent (USD)'].sum():,.2f}")

# Donut Chart - Won vs Lost
st.subheader("Sales Outcome (Won vs Lost)")
crm['Sale Status'] = crm['Lead Status Type'].apply(lambda x: 'Won' if x == 'Sold' else 'Lost')
outcome_counts = crm['Sale Status'].value_counts().reset_index()
fig_donut = px.pie(outcome_counts, names='index', values='Sale Status', hole=0.4,
                   color_discrete_sequence=px.colors.qualitative.Set2)
st.plotly_chart(fig_donut, use_container_width=True)

# CPA by Campaign
st.subheader("Cost Per Acquisition by Campaign")
google_ads['CPA'] = google_ads['Cost'] / google_ads['Conversions'].replace(0, pd.NA)
meta_ads['CPA'] = meta_ads['Amount spent (USD)'] / meta_ads['Leads'].replace(0, pd.NA)
google_ads['Source'] = 'Google'
meta_ads['Source'] = 'Meta'
google_ads.rename(columns={'Campaign': 'Campaign Name'}, inplace=True)
meta_ads.rename(columns={'Ad Name': 'Campaign Name'}, inplace=True)
cpa_data = pd.concat([
    google_ads[['Campaign Name', 'CPA', 'Source']],
    meta_ads[['Campaign Name', 'CPA', 'Source']]
], ignore_index=True).dropna()
fig_cpa = px.bar(cpa_data, x='Campaign Name', y='CPA', color='Source', barmode='group')
st.plotly_chart(fig_cpa, use_container_width=True)

# Cluster Analysis
st.subheader("Lead Clusters")
fig_clusters = px.histogram(clusters, x='Cluster', color='UTM Source', barmode='group')
st.plotly_chart(fig_clusters, use_container_width=True)

# Churn Summary
st.subheader("Churn Summary Insights")
churn_display = churn.reset_index().melt(id_vars='index', var_name='Metric', value_name='Value')
fig_churn = px.bar(churn_display, x='index', y='Value', color='Metric', barmode='group')
st.plotly_chart(fig_churn, use_container_width=True)

st.markdown("Built with Streamlit")
