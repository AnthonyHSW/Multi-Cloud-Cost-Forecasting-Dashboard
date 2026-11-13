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
    st.write("Predict future multi-cloud spend using linear regression on historical billing data.")
    
    # Add an interactive slider for the ML model
    days_to_forecast = st.slider("Forecast Window (Days)", min_value=7, max_value=90, value=30)
    
    if st.button("Generate ML Forecast", type="primary", key="ml_forecast_btn"):
        with st.spinner(f"Running linear regression for the next {days_to_forecast} days..."):
            response = requests.get(f"http://localhost:8000/api/v1/forecast/trend?days={days_to_forecast}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "error" in data:
                    st.error(data["error"])
                else:
                    # --- Metrics Section ---
                    trend_data = data.get("historical_trend", {})
                    col1, col2 = st.columns(2)
                    col1.metric("Spend Trend Direction", trend_data.get("trend_direction", "Unknown"))
                    col2.metric("Daily Growth Rate", f"${trend_data.get('slope', 0.0):.2f} / day")
                    
                    st.divider()
                    
                    # --- Visualization Section ---
                    forecast_list = data.get("forecast", [])
                    if forecast_list:
                        df_forecast = pd.DataFrame(forecast_list)
                        
                        # Build the Plotly Line Chart for the time-series projection
                        fig = px.line(
                            df_forecast, 
                            x="date", 
                            y="predicted_cost", 
                            title=f"{days_to_forecast}-Day Machine Learning Cost Projection",
                            labels={"date": "Date", "predicted_cost": "Predicted Cost ($)"},
                            markers=True
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        fig.update_traces(line_color="#FF4B4B") # Streamlit red for visibility
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("View Raw Projection Data"):
                            st.dataframe(df_forecast, use_container_width=True)
                    else:
                        st.warning("The regression model returned empty data.")
            else:
                st.error("Failed to connect to the Trend Forecasting API.")