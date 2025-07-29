from flask import Blueprint, jsonify
import psutil
from services.threshold_service import get_thresholds

alerts_bp = Blueprint("alerts", __name__)

@alerts_bp.route("/alerts")
def alerts():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    thresholds = get_thresholds()
    cpu_thresh = thresholds.get("cpu", 80)
    mem_thresh = thresholds.get("memory", 80)
    disk_thresh = thresholds.get("disk", 80)

    alerts = []
    if cpu > cpu_thresh:
        alerts.append(f"CPU usage high: {cpu} > {cpu_thresh}")
    if memory > mem_thresh:
        alerts.append(f"Memory usage high: {memory} > {mem_thresh}")
    if disk > disk_thresh:
        alerts.append(f"Disk usage high: {disk} > {disk_thresh}")

    return jsonify({"alerts": alerts}), 200
