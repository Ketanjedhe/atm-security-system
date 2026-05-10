"""
Anomaly Detection Module - Isolation Forest ML model for suspicious ATM transactions
"""
from flask import Blueprint, request, jsonify
from modules.db import transactions_col
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import json

anomaly_bp = Blueprint("anomaly", __name__)

def extract_features(txn):
    """Convert transaction dict to feature vector"""
    try:
        ts = datetime.fromisoformat(txn.get("timestamp", datetime.utcnow().isoformat()))
        hour = ts.hour
    except Exception:
        hour = 12

    amount = float(txn.get("amount", 0))
    # 1=withdrawal, 0=other
    txn_type = 1 if txn.get("type") == "WITHDRAWAL" else 0
    return [amount, hour, txn_type]

def get_training_data():
    """Fetch transactions from DB or use seed data"""
    txns = list(transactions_col.find({}, {"_id": 0}))

    # Always include seed data so model has enough samples
    seed = [
        {"amount": 500,   "timestamp": "2024-01-01T10:00:00", "type": "WITHDRAWAL"},
        {"amount": 1000,  "timestamp": "2024-01-01T11:00:00", "type": "WITHDRAWAL"},
        {"amount": 2000,  "timestamp": "2024-01-01T14:00:00", "type": "WITHDRAWAL"},
        {"amount": 500,   "timestamp": "2024-01-02T09:00:00", "type": "WITHDRAWAL"},
        {"amount": 1500,  "timestamp": "2024-01-02T15:00:00", "type": "WITHDRAWAL"},
        {"amount": 3000,  "timestamp": "2024-01-03T12:00:00", "type": "WITHDRAWAL"},
        {"amount": 800,   "timestamp": "2024-01-03T16:00:00", "type": "WITHDRAWAL"},
        {"amount": 1200,  "timestamp": "2024-01-04T10:30:00", "type": "WITHDRAWAL"},
        {"amount": 700,   "timestamp": "2024-01-04T13:00:00", "type": "WITHDRAWAL"},
        {"amount": 900,   "timestamp": "2024-01-05T11:00:00", "type": "WITHDRAWAL"},
        # Anomalies in seed
        {"amount": 19900, "timestamp": "2024-01-06T03:00:00", "type": "WITHDRAWAL"},
        {"amount": 20000, "timestamp": "2024-01-06T03:05:00", "type": "WITHDRAWAL"},
    ]
    return seed + txns

@anomaly_bp.route("/detect", methods=["POST"])
def detect_anomaly():
    """
    Detect if a given transaction is anomalous using Isolation Forest.
    Body: { "amount": 5000, "timestamp": "2024-01-01T03:00:00", "type": "WITHDRAWAL" }
    """
    data = request.json or {}
    txn = {
        "amount": data.get("amount", 0),
        "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
        "type": data.get("type", "WITHDRAWAL")
    }

    all_txns = get_training_data()
    features = [extract_features(t) for t in all_txns]
    X = np.array(features)

    # Train Isolation Forest
    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(X)

    # Predict on new transaction
    new_features = np.array([extract_features(txn)])
    prediction = model.predict(new_features)[0]   # -1 = anomaly, 1 = normal
    score = model.decision_function(new_features)[0]

    is_anomaly = bool(prediction == -1)
    reasons = []
    amount = float(txn["amount"])

    try:
        hour = datetime.fromisoformat(txn["timestamp"]).hour
    except Exception:
        hour = 12

    if amount > 15000:
        reasons.append(f"Very high withdrawal amount: ₹{amount:,.0f}")
    if hour < 6 or hour > 22:
        reasons.append(f"Transaction at unusual hour: {hour:02d}:00")
    if amount >= 20000:
        reasons.append("Maximum withdrawal limit hit — possible card cloning")
    if amount > 10000 and (hour < 6 or hour > 22):
        reasons.append("High amount combined with off-hours timing — elevated risk")

    return jsonify({
        "transaction": txn,
        "is_anomaly": is_anomaly,
        "anomaly_score": round(float(score), 4),
        "risk_level": "High" if is_anomaly else "Normal",
        "reasons": reasons if reasons else (["Transaction appears normal"] if not is_anomaly else ["Flagged by ML model"]),
        "recommendation": "Flag for manual review and notify cardholder" if is_anomaly else "No action required"
    }), 200

@anomaly_bp.route("/analyze-all", methods=["GET"])
def analyze_all():
    """Run anomaly detection on all stored transactions"""
    all_txns = get_training_data()
    if len(all_txns) < 5:
        return jsonify({"error": "Not enough transaction data"}), 400

    features = [extract_features(t) for t in all_txns]
    X = np.array(features)

    model = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
    model.fit(X)
    predictions = model.predict(X)
    scores = model.decision_function(X)

    results = []
    for i, txn in enumerate(all_txns):
        results.append({
            "transaction": txn,
            "is_anomaly": bool(predictions[i] == -1),
            "score": round(float(scores[i]), 4)
        })

    anomalies = [r for r in results if r["is_anomaly"]]
    return jsonify({
        "total_analyzed": len(results),
        "anomalies_found": len(anomalies),
        "anomalies": anomalies,
        "all_results": results
    }), 200
