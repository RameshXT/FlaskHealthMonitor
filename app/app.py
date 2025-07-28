from flask import Flask, request, jsonify
import psutil
import psycopg2
import json
import datetime
import threading
import time
import redis
import os

# POSTGRES CONFIG
DB_CONFIG = {
    "dbname": "monitoringdb",
    "user": "postgres",
    "password": "clear",
    "host": "localhost",
    "port": 5432
}

# REDIS CONFIG
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# POSTGRES CONNECTION
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# TABLE CREATION
def initialize_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS system_metrics (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP,
            cpu_percent REAL,
            memory_percent REAL,
            disk_percent REAL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS thresholds (
            name TEXT PRIMARY KEY,
            value REAL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# BACKGROUND THREAD TO COLLECT SYSTEM METRICS
def collect_metrics_background():
    while True:
        timestamp = datetime.datetime.now()
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO system_metrics (timestamp, cpu_percent, memory_percent, disk_percent)
                VALUES (%s, %s, %s, %s)
            """, (timestamp, cpu, memory, disk))
            conn.commit()
        finally:
            cur.close()
            conn.close()

        print(f"[{timestamp}] Metrics inserted.")
        time.sleep(60)

# FLASK APP
def create_app():
    app = Flask(__name__)
    initialize_db()

    thread = threading.Thread(target=collect_metrics_background, daemon=True)
    thread.start()

    # HEALTH ENDPOINT
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    # METRICS ENDPOINT
    @app.route("/metrics")
    def metrics():
        timestamp = datetime.datetime.now()
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        # SAVE TO REDIS
        r.hset("latest_metrics", mapping={
            "timestamp": timestamp.isoformat(),
            "cpu_percent": cpu,
            "memory_percent": memory,
            "disk_percent": disk
        })

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO system_metrics (timestamp, cpu_percent, memory_percent, disk_percent)
                VALUES (%s, %s, %s, %s)
            """, (timestamp, cpu, memory, disk))
            conn.commit()
        finally:
            cur.close()
            conn.close()

        return jsonify({
            "timestamp": timestamp.isoformat(),
            "cpu_percent": cpu,
            "memory_percent": memory,
            "disk_percent": disk
        }), 200

    # THRESHOLDS ENDPOINT
    @app.route("/thresholds", methods=["GET", "POST"])
    def thresholds():
        conn = get_db_connection()
        cur = conn.cursor()
        if request.method == "POST":
            data = request.get_json()
            for key in ["cpu", "memory", "disk"]:
                if key in data:
                    cur.execute("""
                        INSERT INTO thresholds (name, value)
                        VALUES (%s, %s)
                        ON CONFLICT (name) DO UPDATE SET value = EXCLUDED.value
                    """, (key, float(data[key])))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"message": "Thresholds updated"}), 200
        else:
            cur.execute("SELECT name, value FROM thresholds")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return jsonify({name: value for name, value in rows}), 200

    # ALERTS ENDPOINT
    @app.route("/alerts")
    def alerts():
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, value FROM thresholds")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        thresholds = {name: value for name, value in rows}
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

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)