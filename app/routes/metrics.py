from flask import Blueprint, jsonify
from services.monitor_service import collect_current_metrics, insert_metrics_into_db
from extensions.redis_client import redis_client

metrics_bp = Blueprint("metrics", __name__)

@metrics_bp.route("/metrics")
def metrics():
    data = collect_current_metrics()
    
    redis_client.hset("latest_metrics", mapping={
        "timestamp": data["timestamp"].isoformat(),
        "cpu_percent": data["cpu_percent"],
        "memory_percent": data["memory_percent"],
        "disk_percent": data["disk_percent"]
    })

    insert_metrics_into_db(data["timestamp"], data["cpu_percent"], data["memory_percent"], data["disk_percent"])

    return jsonify(data), 200
