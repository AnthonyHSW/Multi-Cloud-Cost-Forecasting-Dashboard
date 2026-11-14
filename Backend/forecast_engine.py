# Anthony Wong
# Email: Anw2727@gmail.com
# Multi-Cloud Cost Forecasting Engine

import sqlite3
import pandas as pd
import numpy as np
from datetime import timedelta

def generate_cost_forecast(db_path: str, days_to_predict: int = 30):
    # 1. Fetch historical daily spend from SQLite
    conn = sqlite3.connect(db_path)
    
    # Adjust table/column names to match your schema
    query = """
        SELECT date(timestamp) as ds, SUM(cost) as total_cost
        FROM cloud_resources
        GROUP BY ds
        ORDER BY ds ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return {"error": "No historical data found to generate a forecast."}
    
    # Convert string dates to datetime objects
    df['ds'] = pd.to_datetime(df['ds'])
    
    # 2. Convert dates to numerical values (ordinal) for linear regression
    df['date_ordinal'] = df['ds'].map(pd.Timestamp.toordinal)
    
    # 3. Fit the linear regression model (y = mx + b)
    # x = dates, y = costs. The '1' means we want a 1st-degree polynomial (a straight line)
    x = df['date_ordinal'].values
    y = df['total_cost'].values
    slope, intercept = np.polyfit(x, y, 1)
    
    # 4. Generate future dates and predictions
    last_date = df['ds'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, days_to_predict + 1)]
    future_ordinals = np.array([d.toordinal() for d in future_dates])
    
    # Calculate predicted costs: (slope * future_date) + intercept
    future_predictions = (slope * future_ordinals) + intercept
    
    # Ensure we don't predict negative costs (floor it at $0)
    future_predictions = np.maximum(future_predictions, 0)
    
    # 5. Format the output for your FastAPI endpoint
    forecast_data = [
        {
            "date": date.strftime('%Y-%m-%d'),
            "predicted_cost": round(cost, 2)
        }
        for date, cost in zip(future_dates, future_predictions)
    ]
    
    return {
        "historical_trend": {
            "slope": round(slope, 4),
            "trend_direction": "Increasing" if slope > 0 else "Decreasing"
        },
        "forecast": forecast_data
    }
