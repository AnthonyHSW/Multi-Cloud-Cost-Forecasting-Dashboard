from fastapi import FastAPI
from pydantic import BaseModel
from auditor_engine import run_audit
from database import get_projected_costs

app = FastAPI(title="Multi-Cloud Cost API")

class CloudCost(BaseModel):
    cloud_provider: str
    projected_monthly_cost: float

@app.get("/api/v1/audit/idle-resources")
def get_idle_resources_audit():
    """Triggers the auditor engine to flag idle VMs."""
    return run_audit()

@app.get("/api/v1/forecast", response_model=list[CloudCost])
def get_cost_forecast():
    """Fetches the 30-day projected costs grouped by provider."""
    return get_projected_costs()