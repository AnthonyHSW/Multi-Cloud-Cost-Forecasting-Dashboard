import sqlite3
import random
from datetime import datetime, timedelta

def setup_mock_database():
    conn = sqlite3.connect("cloud_resources.db")
    cursor = conn.cursor()

    # 1. Create the instances table (for the Auditor Engine)
    cursor.execute("DROP TABLE IF EXISTS instances")
    cursor.execute("""
        CREATE TABLE instances (
            instance_id TEXT PRIMARY KEY,
            provider TEXT,
            instance_type TEXT,
            status TEXT,
            cpu_utilization REAL,
            hourly_rate REAL,
            resources_tag TEXT
        )
    """)

    # Insert mock instances (some idle, some active)
    mock_instances = [
        ("i-0abcd1234efgh5678", "aws", "t3.medium", "running", 2.1, 0.041, "Marketing-website"),   # Idle
        ("i-0wxyz9876vuts5432", "aws", "m5.large", "running", 65.0, 0.096, "default_tag"),   # Active
        ("vm-azure-prod-01", "azure", "Standard_D2s_v3", "running", 1.5, 0.08, "default_tag"),# Idle
        ("vm-azure-dev-02", "azure", "Standard_B2s", "stopped", 0.0, 0.04, "data-science-pipeline"),   # Stopped
        ("gcp-instance-1", "gcp", "e2-medium", "running", 82.4, 0.033, "default_tag"),       # Active
        ("gcp-instance-2", "gcp", "n1-standard-1", "running", 3.8, 0.047, "backend-api")     # Idle
    ]
    cursor.executemany("""
        INSERT INTO instances (instance_id, provider, instance_type, status, cpu_utilization, hourly_rate, resources_tag)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, mock_instances)

    # 2. Create the cloud_resources table (for the Forecasting Engine)
    cursor.execute("DROP TABLE IF EXISTS cloud_resources")
    cursor.execute("""
        CREATE TABLE cloud_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cost REAL,
            resources_tag TEXT
        )
    """)

    # Generate 60 days of historical daily spend data
    today = datetime.now()
    historical_costs = []
    base_cost = 150.0

    for i in range(60, 0, -1):
        record_date = (today - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")
        # Add a slight upward trend with some random noise
        daily_cost = base_cost + (60 - i) * 0.5 + random.uniform(-10.0, 15.0)
        historical_costs.append((record_date, round(daily_cost, 2)))

    cursor.executemany("INSERT INTO cloud_resources (timestamp, cost, resources_tag) VALUES (?, ?, ?)", [(ts, cost, "default_tag") for ts, cost in historical_costs])

    conn.commit()
    conn.close()
    print("✅ Successfully generated mock data in cloud_resources.db")
    print(" - Created 'instances' table with 6 VMs")
    print(" - Created 'cloud_resources' table with 60 days of cost history")

if __name__ == "__main__":
    setup_mock_database()