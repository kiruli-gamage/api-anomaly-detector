import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pickle
import numpy as np
from detector import AnomalyDetector
from generator import generate_api_traffic

print("Pre-training anomaly detector on 500 data points...")

detector = AnomalyDetector()

for i in range(500):
    point = generate_api_traffic(inject_anomaly=False)
    detector.add_datapoint(point)

detector.train()

model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'detector.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(detector, f)

print("Done! Model saved to models/detector.pkl")
print(f"Trained on 500 normal data points.")
print("Anomaly detection is now instant from startup.")