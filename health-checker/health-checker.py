import requests
import configparser
from utils.alert import send_alert
from utils.k8s_utils import restart_pod

# Load config
config = configparser.ConfigParser()
config.read("config.ini")

endpoints = config['APP']['endpoints'].split(',')
webhook = config['ALERT']['webhook_url']
label_selector = config['K8S']['label_selector']
namespace = config['K8S']['namespace']

def check_endpoints():
    for url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                raise Exception(f"Status: {response.status_code}")
        except Exception as e:
            msg = f":rotating_light: HEALTH CHECK FAILED\nURL: {url}\nReason: {e}"
            print(msg)
            send_alert(msg, webhook)
            restart_pod(label_selector, namespace)

if __name__ == "__main__":
    check_endpoints()
