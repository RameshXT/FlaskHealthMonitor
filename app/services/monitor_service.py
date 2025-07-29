import datetime
import psutil
from models.db import get_db_connection

def collect_current_metrics():
    return {
        "timestamp": datetime.datetime.now(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
}

def insert_metrics_into_db(timestamp, cpu, memory, disk):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO system_metrics (timestamp, cpu_percent, memory_percent, disk_percent)
        VALUES (%s, %s, %s, %s)
    """, (timestamp, cpu, memory, disk))
    conn.commit()
    cur.close()
    conn.close()
