# Anthony Wong
# Email: Anw2727@gmail.com
# Multi-Cloud Cost Forecasting Dashboard

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="FinOps Cloud Dashboard", layout="wide")
st.title("☁️ Multi-Cloud Cost Dashboard")

# Create two tabs for the two core product features
tab1, tab2 = st.tabs(["Auditor Engine (Idle VMs)", "Cost Forecasting"])

# --- TAB 1: AUDITOR ENGINE ---
with tab1:
    st.write("Detect idle virtual machines across AWS, Azure, and GCP to forecast potential cost savings.")
    
    if st.button("Run Infrastructure Audit", type="primary"):
        with st.spinner("Analyzing multi-cloud resources..."):
            response = requests.get("http://localhost:8000/api/v1/audit/idle-resources")
            
            if response.status_code == 200:
                data = response.json()
                impact = data.get("financial_impact", {})
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Idle Instances Flagged", impact.get("total_idle_instances", 0))
                col2.metric("Daily Wasted Spend", f"${impact.get('projected_daily_savings', 0.0):.2f}")
                col3.metric("Monthly Wasted Spend", f"${impact.get('projected_monthly_savings', 0.0):.2f}")
                
                st.divider()
                instances = data.get("flagged_instances", [])
                if instances:
                    df = pd.DataFrame(instances)[["provider", "instance_id", "status", "cpu_utilization", "hourly_rate"]]
                    st.dataframe(df, use_container_width=True)
                else:
                    st.success("No idle instances found.")
            else:
                st.error("Failed to connect to Auditor API.")

# --- TAB 2: FORECASTING ENGINE ---
with tab2:
    st.write("Projected 30-day cumulative costs based on active instances by provider.")
    
    if st.button("Generate Forecast", type="primary", key="forecast_btn"):
        with st.spinner("Calculating projections..."):
            response = requests.get("http://localhost:8000/api/v1/forecast")
            
            if response.status_code == 200:
                forecast_data = response.json()
                
                if forecast_data:
                    df_forecast = pd.DataFrame(forecast_data)
                    
                    # Capitalize provider names for the chart
                    df_forecast['cloud_provider'] = df_forecast['cloud_provider'].str.upper()
                    
                    # Build a Plotly Bar Chart
                    fig = px.bar(
                        df_forecast, 
                        x="cloud_provider", 
                        y="projected_monthly_cost",
                        title="30-Day Cost Projection by Provider",
                        labels={"cloud_provider": "Cloud Provider", "projected_monthly_cost": "Projected Cost ($)"},
                        color="cloud_provider",
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No active instances found to project costs.")
            else:
                st.error("Failed to connect to Forecasting API.")