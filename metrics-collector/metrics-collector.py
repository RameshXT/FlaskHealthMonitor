import os
import psutil
import time
import logging
from datetime import datetime
from prometheus_client import Gauge, start_http_server

# === Setup project base directory ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "../logs")
REPORT_DIR = os.path.join(BASE_DIR, "../reports")

# === Create directories if they don't exist ===
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# === Logging Setup ===
log_file_path = os.path.join(LOG_DIR, "metrics_collector.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# === Prometheus Metrics Setup ===
cpu_usage_gauge = Gauge('system_cpu_usage_percent', 'System CPU usage in percent')
memory_usage_gauge = Gauge('system_memory_usage_percent', 'System Memory usage in percent')
disk_usage_gauge = Gauge('system_disk_usage_percent', 'System Disk usage in percent')
net_sent_gauge = Gauge('network_bytes_sent', 'Network bytes sent')
net_recv_gauge = Gauge('network_bytes_received', 'Network bytes received')


def collect_metrics():
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        net = psutil.net_io_counters()

        cpu_usage_gauge.set(cpu)
        memory_usage_gauge.set(memory)
        disk_usage_gauge.set(disk)
        net_sent_gauge.set(net.bytes_sent)
        net_recv_gauge.set(net.bytes_recv)

        logging.info(f"Collected metrics: CPU={cpu}%, Memory={memory}%, Disk={disk}%, NetSent={net.bytes_sent}, NetRecv={net.bytes_recv}")
    
    except Exception as e:
        logging.error(f"Error collecting metrics: {e}")


def write_report_to_file():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(REPORT_DIR, f"metrics_{timestamp}.txt")

        with open(filename, "w") as f:
            f.write(f"CPU Usage: {psutil.cpu_percent()}%\n")
            f.write(f"Memory Usage: {psutil.virtual_memory().percent}%\n")
            f.write(f"Disk Usage: {psutil.disk_usage('/').percent}%\n")
            net = psutil.net_io_counters()
            f.write(f"Network Sent: {net.bytes_sent}\n")
            f.write(f"Network Received: {net.bytes_recv}\n")

        logging.info(f"Metrics report written to {filename}")
    
    except Exception as e:
        logging.error(f"Error writing metrics report: {e}")


if __name__ == "__main__":
    start_http_server(8000)
    logging.info("Started Prometheus metrics server on port 8000")

    while True:
        collect_metrics()
        write_report_to_file()  # Optional: Comment out if not needed
        time.sleep(60)
