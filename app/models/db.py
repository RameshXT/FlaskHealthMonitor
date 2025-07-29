import os
import psycopg2
from config import *

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT"))
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

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
    print("Database initialized successfully.")