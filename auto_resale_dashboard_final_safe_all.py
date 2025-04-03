
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

# Ensure cost columns are float
google_ads.columns = [col.strip() for col in google_ads.columns]
meta_ads.columns = [col.strip() for col in meta_ads.columns]

google_ads['Cost'] = google_ads['Cost'].replace('[\$,]', '', regex=True).astype(float)
meta_ads['Amount spent (USD)'] = meta_ads['Amount spent (USD)'].replace('[\$,]', '', regex=True).astype(float)

# Overview KPIs
st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Leads", len(crm))
col2.metric("Total Sold", crm['Lead Status Type'].eq('Sold').sum())
total_spend = google_ads['Cost'].sum() + meta_ads['Amount spent (USD)'].sum()
col3.metric("Total Google + Meta Spend", f"${total_spend:,.2f}")

# Donut Chart - Won vs Lost
st.subheader("Sales Outcome (Won vs Lost)")
crm['Sale Status'] = crm['Lead Status Type'].apply(lambda x: 'Won' if x == 'Sold' else 'Lost')
outcome_counts = crm['Sale Status'].value_counts().reset_index()
outcome_counts.columns = ['Sale Status', 'Count']
fig_donut = px.pie(outcome_counts, names='Sale Status', values='Count', hole=0.4,
                   color_discrete_sequence=px.colors.qualitative.Set2)
st.plotly_chart(fig_donut, use_container_width=True)

# CPA by Campaign (Google + Meta)
st.subheader("Cost Per Acquisition by Campaign")

# Google CPA
google_ads['CPA'] = google_ads['Cost'] / google_ads['Conversions'].replace(0, pd.NA)
google_ads['Source'] = 'Google'

google_campaign_col = next((col for col in google_ads.columns if 'campaign' in col.lower()), None)
meta_campaign_col = next((col for col in meta_ads.columns if 'campaign' in col.lower() or 'ad name' in col.lower()), None)

# Meta CPA with fallback on leads column
possible_leads_columns = ['Leads', 'Results', 'Leads (form)', 'Leads (conversion)']
meta_leads_column = next((col for col in meta_ads.columns if col in possible_leads_columns), None)

if google_campaign_col and meta_campaign_col and meta_leads_column:
    google_ads.rename(columns={google_campaign_col: 'Campaign Name'}, inplace=True)
    meta_ads.rename(columns={meta_campaign_col: 'Campaign Name'}, inplace=True)
    meta_ads['CPA'] = meta_ads['Amount spent (USD)'] / meta_ads[meta_leads_column].replace(0, pd.NA)
    meta_ads['Source'] = 'Meta'

    cpa_data = pd.concat([
        google_ads[['Campaign Name', 'CPA', 'Source']],
        meta_ads[['Campaign Name', 'CPA', 'Source']]
    ], ignore_index=True).dropna()

    fig_cpa = px.bar(cpa_data, x='Campaign Name', y='CPA', color='Source', barmode='group')
    st.plotly_chart(fig_cpa, use_container_width=True)
else:
    st.warning("Campaign name or leads column missing from Google or Meta Ads data. CPA chart not displayed.")

# Cluster Analysis
st.subheader("Lead Clusters")
if 'Cluster' in clusters.columns:
    fig_clusters = px.histogram(clusters, x='Cluster', color='UTM Source', barmode='group')
    st.plotly_chart(fig_clusters, use_container_width=True)
else:
    st.warning("Cluster data not found in uploaded file.")

# Churn Summary
st.subheader("Churn Summary Insights")
churn.columns = [col.strip() for col in churn.columns]
churn_display = churn.reset_index().melt(id_vars='index', var_name='Metric', value_name='Value')
fig_churn = px.bar(churn_display, x='index', y='Value', color='Metric', barmode='group')
st.plotly_chart(fig_churn, use_container_width=True)

st.markdown("Built with Streamlit")
