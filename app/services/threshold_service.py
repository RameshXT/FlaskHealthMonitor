from models.db import get_db_connection

def update_thresholds(data):
    conn = get_db_connection()
    cur = conn.cursor()
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

def get_thresholds():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, value FROM thresholds")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {name: value for name, value in rows}
