#Author: Anthony Wong
#Email: Anw2727@gmail.com
#auditor_engine.py.

import sqlite3
from typing import List, Dict, Any

DB_PATH = "cloud_resources.db" 

def fetch_idle_instances(cpu_threshold: float = 5.0) -> List[Dict[str, Any]]:
    """
    Queries the database for running VMs across all providers that 
    have a CPU utilization below the specified threshold.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Returns rows as dictionaries instead of tuples
    cursor = conn.cursor()

    # NOTE: Adjust table and column names (e.g., 'virtual_machines', 'status', 
    # 'cpu_utilization', 'hourly_rate') to match your actual SQLite schema.
    query = """
        SELECT 
            instance_id, 
            provider, 
            instance_type,
            status, 
            cpu_utilization, 
            hourly_rate
        FROM 
            virtual_machines
        WHERE 
            status = 'running' 
            AND cpu_utilization <= ?
    """
    
    try:
        cursor.execute(query, (cpu_threshold,))
        idle_vms = [dict(row) for row in cursor.fetchall()]
        return idle_vms
    finally:
        conn.close()

def calculate_wasted_spend(idle_instances: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates the financial impact of the idle instances.
    Projects daily and monthly savings.
    """
    total_hourly_waste = sum(vm.get('hourly_rate', 0.0) for vm in idle_instances)
    
    daily_savings = total_hourly_waste * 24
    monthly_savings = daily_savings * 30  # Standardized 30-day billing month
    
    # Grouping waste by provider for better dashboard visualizations later
    provider_breakdown = {"aws": 0.0, "azure": 0.0, "gcp": 0.0}
    for vm in idle_instances:
        provider = vm.get('provider', '').lower()
        if provider in provider_breakdown:
            provider_breakdown[provider] += vm.get('hourly_rate', 0.0) * 24 * 30
            
    return {
        "total_idle_instances": len(idle_instances),
        "projected_daily_savings": round(daily_savings, 2),
        "projected_monthly_savings": round(monthly_savings, 2),
        "savings_by_provider_monthly": {k: round(v, 2) for k, v in provider_breakdown.items()}
    }

def run_audit() -> Dict[str, Any]:
    """
    Main orchestration function to be called by your FastAPI endpoint.
    """
    idle_vms = fetch_idle_instances(cpu_threshold=5.0)
    financial_impact = calculate_wasted_spend(idle_vms)
    
    return {
        "audit_status": "success",
        "financial_impact": financial_impact,
        "flagged_instances": idle_vms
    }