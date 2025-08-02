from kubernetes import client, config
import traceback

def restart_pod(label_selector: str, namespace: str = "default"):
    try:
        # Use config.load_kube_config() for local, incluster for pod
        config.load_kube_config()  # Replace with load_incluster_config() if inside cluster
        v1 = client.CoreV1Api()
        pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)

        for pod in pods.items:
            pod_name = pod.metadata.name
            print(f"[INFO] Deleting pod {pod_name} in {namespace}")
            v1.delete_namespaced_pod(pod_name, namespace)
    except Exception as e:
        print("[ERROR] Failed to restart pod:", traceback.format_exc())
