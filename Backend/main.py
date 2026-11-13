from fastapi import FastAPI
from auditor_engine import run_audit

app = FastAPI()

@app.get("/api/v1/audit/idle-resources")
def get_idle_resources_audit():
    """
    Endpoint that triggers the auditor engine and returns the financial analysis.
    """
    audit_results = run_audit()
    print(audit_results)
    return audit_results