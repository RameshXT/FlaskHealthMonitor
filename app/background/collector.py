import threading
import time
from services.monitor_service import collect_current_metrics, insert_metrics_into_db

def collect_metrics_background():
    while True:
        data = collect_current_metrics()
        insert_metrics_into_db(data["timestamp"], data["cpu_percent"], data["memory_percent"], data["disk_percent"])
        print(f"[{data['timestamp']}] Metrics inserted.")
        time.sleep(60)

def start_metric_collector():
    thread = threading.Thread(target=collect_metrics_background, daemon=True)
    thread.start()
