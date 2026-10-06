# Author: Anthony Wong
# Email: Anw2727@gmail.com
# database.py

import sqlite3

DATABASE_PATH = "cloud_resources.db"

def get_projected_costs():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Calculate the 30-day projection (720 hours) only for active VMs
    query = """
        SELECT 
            provider AS cloud_provider, 
            SUM(hourly_rate) * 720 AS projected_monthly_cost
        FROM instances 
        WHERE status = 'running'
        GROUP BY provider;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    # Convert the SQLite Row objects into a list of dictionaries
    return [dict(row) for row in rows]