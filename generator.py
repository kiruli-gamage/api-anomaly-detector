import numpy as np
from datetime import datetime
import random


def generate_api_traffic(inject_anomaly=False):
    now = datetime.now()

    latency = np.random.normal(120, 15)
    requests_per_sec = np.random.normal(50, 8)
    error_rate = np.random.uniform(0, 0.02)
    cpu_usage = np.random.normal(40, 5)

    if inject_anomaly:
        anomaly_type = random.choice(['latency_spike', 'traffic_surge', 'error_burst'])
        if anomaly_type == 'latency_spike':
            latency = np.random.normal(800, 50)
        elif anomaly_type == 'traffic_surge':
            requests_per_sec = np.random.normal(300, 20)
        elif anomaly_type == 'error_burst':
            error_rate = np.random.uniform(0.3, 0.8)

    return {
        'timestamp': now.strftime('%H:%M:%S'),
        'latency_ms': round(max(0, latency), 2),
        'requests_per_sec': round(max(0, requests_per_sec), 2),
        'error_rate': round(max(0, error_rate), 4),
        'cpu_usage': round(max(0, min(100, cpu_usage)), 2),
        'anomaly_injected': inject_anomaly
    }