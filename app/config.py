import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT",
    "REDIS_HOST", "REDIS_PORT"
]

for var in required_vars:
    if not os.getenv(var):
        raise RuntimeError(f"Missing required environment variable: {var}")
