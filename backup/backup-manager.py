import os
import subprocess
from datetime import datetime
import logging
from dotenv import load_dotenv
import time

# === Load .env ===
dotenv_path = '/home/ec2-user/test/FlaskHealthMonitor/.env'
load_dotenv(dotenv_path)

# === Configs from ENV ===
LOG_DIR = '/home/ec2-user/test/FlaskHealthMonitor/logs'
SNAPSHOT_DIR = '/home/ec2-user/test/FlaskHealthMonitor/snapshot'

# PostgreSQL
PG_DB = os.getenv('DB_NAME')
PG_USER = os.getenv('DB_USER')
PG_PASSWORD = os.getenv('DB_PASSWORD')
PG_HOST = os.getenv('DB_HOST')
PG_PORT = os.getenv('DB_PORT', '5432')

# Redis
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

# === Logging Setup ===
logging.basicConfig(
    filename=os.path.join(LOG_DIR, 'backup.log'),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def backup_postgres():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_file = os.path.join(SNAPSHOT_DIR, f'postgres_backup_{timestamp}.sql')

    try:
        cmd = [
            'pg_dump',
            f'-U{PG_USER}',
            f'-h{PG_HOST}',
            f'-p{PG_PORT}',
            PG_DB
        ]

        env = os.environ.copy()
        env['PGPASSWORD'] = PG_PASSWORD

        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env, check=True)

        logging.info(f"✅ PostgreSQL backup completed: {backup_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ PostgreSQL backup failed: {e.stderr.decode().strip()}")


def backup_redis():
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    snapshot_file = os.path.join(SNAPSHOT_DIR, f'redis_dump_{timestamp}.rdb')

    try:
        # Trigger Redis snapshot
        subprocess.run(['redis-cli', '-h', REDIS_HOST, '-p', REDIS_PORT, 'BGSAVE'], check=True)

        time.sleep(5)  # Wait for Redis to write dump.rdb

        dump_path = '/var/lib/redis/dump.rdb'
        if os.path.exists(dump_path):
            subprocess.run(['cp', dump_path, snapshot_file], check=True)
            logging.info(f"✅ Redis snapshot saved: {snapshot_file}")
        else:
            logging.error("❌ Redis dump.rdb not found!")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Redis snapshot failed: {e.stderr.decode().strip()}")


if __name__ == "__main__":
    logging.info("=== 🔁 Backup Started ===")
    backup_postgres()
    backup_redis()
    logging.info("=== ✅ Backup Completed ===")
