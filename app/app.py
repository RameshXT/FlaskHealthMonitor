from flask import Flask, request, jsonify
import os
import time
import datetime
import threading
import psutil
import redis
import psycopg2

from dotenv import load_dotenv

# LOAD ENV
load_dotenv()

# REQUIRED ENV KEYS 
required_env_vars = [
    "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "REDIS_HOST", "REDIS_PORT"
]

# VALIDATE ALL REQUIRED ENV VARIABLES
for var in required_env_vars:
    if not os.getenv(var):
        raise RuntimeError(f"Missing required environment variable: {var}")

# POSTGRES CONFIG
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT"))
}

# REDIS CONFIG
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=0,
    decode_responses=True
)

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
        redis_client.hset("latest_metrics", mapping={
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
