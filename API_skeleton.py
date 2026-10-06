# Author: Anthony Wong
# Email: Anw2727@gmail.com
# API_skeleton

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title = "Cloud Cost Forecasting API")

class CloudCost(BaseModel):
    cloud_provider: str
    projected_monthly_cost: float

@app.get("/")
def read_root():
    return {"status": "API is running"}

@app.get("/api/v1/forecast", response_model=list[CloudCost])
def get_cost_forecast():
    return [
        {"cloud_provider": "AWS", "projected_monthly_cost": 450.25},
        {"cloud_provider": "Azure", "projected_monthly_cost": 320.50}
    ]
