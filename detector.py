import numpy as np
import pickle
import os
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.05,
            random_state=42,
            n_estimators=100
        )
        self.is_trained = False
        self.history = []

    def load_pretrained(self):
        model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'detector.pkl')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                pretrained = pickle.load(f)
                self.model = pretrained.model
                self.history = pretrained.history
                self.is_trained = True
                print("Pre-trained model loaded — detection is instant!")
                return True
        return False

    def add_datapoint(self, datapoint):
        self.history.append([
            datapoint['latency_ms'],
            datapoint['requests_per_sec'],
            datapoint['error_rate'],
            datapoint['cpu_usage']
        ])

    def train(self):
        if len(self.history) >= 50:
            self.model.fit(self.history)
            self.is_trained = True

    def predict(self, datapoint):
        if not self.is_trained:
            return False, 0.0

        features = [[
            datapoint['latency_ms'],
            datapoint['requests_per_sec'],
            datapoint['error_rate'],
            datapoint['cpu_usage']
        ]]

        prediction = self.model.predict(features)[0]
        score = self.model.score_samples(features)[0]

        is_anomaly = prediction == -1
        confidence = round((1 - (score + 0.5)) * 100, 1)

        return is_anomaly, confidence