from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List

# Import your service function (adjust the import path to match your structure)
from forecast_engine import generate_cost_forecast

# Initialize the router
router = APIRouter(
    prefix="/api/v1/forecast",
    tags=["Forecasting"]
)

# Define Pydantic models for the response structure
class TrendData(BaseModel):
    slope: float
    trend_direction: str

class ForecastDay(BaseModel):
    date: str
    predicted_cost: float

class ForecastResponse(BaseModel):
    historical_trend: TrendData
    forecast: List[ForecastDay]

# Create the GET endpoint
@router.get("/costs", response_model=ForecastResponse)
def get_cost_forecast(
    days: int = Query(30, ge=1, le=90, description="Number of days to forecast into the future")
):
    try:
        # Call the service layer function
        # Replace 'cloud_data.db' with your actual SQLite file path or database dependency
        result = generate_cost_forecast("cloud_resources.db", days_to_predict=days)
        
        # Check if the service layer returned our custom error string
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
            
        return result
        
    except Exception as e:
        # Catch unexpected errors (like missing tables or locked DBs)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")