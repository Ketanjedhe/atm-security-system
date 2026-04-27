"""
Standalone Anomaly Detection Script
Tests the Isolation Forest model on sample ATM transactions
Usage: python security/anomaly_standalone.py
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime

# Sample training data: [amount, hour_of_day, is_withdrawal]
TRAINING_DATA = [
    [500,   10, 1], [1000, 11, 1], [2000, 14, 1], [500,  9,  1],
    [1500, 15, 1],  [3000, 12, 1], [800,  16, 1], [1200, 10, 1],
    [700,  13, 1],  [900,  11, 1], [600,  14, 1], [1100, 15, 1],
    [400,   9, 1],  [2500, 13, 1], [1800, 16, 1],
]

TEST_TRANSACTIONS = [
    {"amount": 500,   "hour": 10, "type": "WITHDRAWAL", "label": "Normal"},
    {"amount": 1000,  "hour": 14, "type": "WITHDRAWAL", "label": "Normal"},
    {"amount": 19900, "hour": 3,  "type": "WITHDRAWAL", "label": "Suspicious - High amount + odd hour"},
    {"amount": 20000, "hour": 3,  "type": "WITHDRAWAL", "label": "Suspicious - Max limit at 3AM"},
    {"amount": 15000, "hour": 2,  "type": "WITHDRAWAL", "label": "Suspicious - Large amount at 2AM"},
    {"amount": 200,   "hour": 23, "type": "WITHDRAWAL", "label": "Borderline - Late night small amount"},
]

def main():
    print("=" * 60)
    print("  ATM Anomaly Detection - Isolation Forest Model")
    print("=" * 60)

    X_train = np.array(TRAINING_DATA)
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(X_train)
    print(f"\n[+] Model trained on {len(TRAINING_DATA)} transactions\n")

    print(f"{'Amount':>8} {'Hour':>5} {'Prediction':>12} {'Score':>8}  Label")
    print("-" * 70)

    for txn in TEST_TRANSACTIONS:
        features = np.array([[txn["amount"], txn["hour"], 1]])
        pred = model.predict(features)[0]
        score = model.decision_function(features)[0]
        is_anomaly = pred == -1
        flag = "⚠️  ANOMALY" if is_anomaly else "✅ Normal  "
        print(f"₹{txn['amount']:>7} {txn['hour']:>5}h {flag} {score:>8.4f}  {txn['label']}")

    print("\n[+] Anomaly detection complete.")
    print("    Negative scores = more anomalous. Threshold ≈ 0.0")

if __name__ == "__main__":
    main()
