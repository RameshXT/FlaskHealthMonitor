import requests

def send_alert(message: str, webhook_url: str):
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to send alert: {e}")
