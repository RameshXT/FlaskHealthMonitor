import requests
import time

# FLASK APP HEALTH CHECK
URL = "http://localhost:5000/health"
TIMEOUT = 5

try:
    response = requests.get(URL, timeout=TIMEOUT)
    if response.status_code == 200:
        print(f"[{time.ctime()}] Application is UP")
    else:
        print(f"[{time.ctime()}] Application is DOWN! Status code: {response.status_code}")
except requests.RequestException as e:
    print(f"[{time.ctime()}] Application is DOWN! Error: {e}")
