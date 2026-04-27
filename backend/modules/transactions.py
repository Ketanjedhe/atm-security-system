"""
Transaction module - Balance check, withdrawal, mini statement
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.db import users_col, transactions_col, logs_col
from bson import ObjectId
from datetime import datetime

transactions_bp = Blueprint("transactions", __name__)

def log_event(event_type, user_id, details):
    logs_col.insert_one({
        "event_type": event_type,
        "user_id": user_id,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    })

@transactions_bp.route("/balance", methods=["GET"])
@jwt_required()
def get_balance():
    user_id = get_jwt_identity()
    user = users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    log_event("BALANCE_CHECK", user_id, "Balance enquiry")
    return jsonify({"balance": user["balance"], "name": user["name"]}), 200

@transactions_bp.route("/withdraw", methods=["POST"])
@jwt_required()
def withdraw():
    user_id = get_jwt_identity()
    data = request.json
    amount = data.get("amount", 0)

    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    if amount > 20000:
        return jsonify({"error": "Withdrawal limit is ₹20,000 per transaction"}), 400
    if amount % 100 != 0:
        return jsonify({"error": "Amount must be in multiples of ₹100"}), 400

    user = users_col.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user["balance"] < amount:
        log_event("INSUFFICIENT_FUNDS", user_id, f"Attempted ₹{amount}, balance ₹{user['balance']}")
        return jsonify({"error": "Insufficient balance"}), 400

    new_balance = user["balance"] - amount
    users_col.update_one({"_id": ObjectId(user_id)}, {"$set": {"balance": new_balance}})

    txn = {
        "user_id": user_id,
        "type": "WITHDRAWAL",
        "amount": amount,
        "balance_after": new_balance,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "SUCCESS"
    }
    transactions_col.insert_one(txn)
    log_event("WITHDRAWAL", user_id, f"Withdrew ₹{amount}. New balance: ₹{new_balance}")

    return jsonify({
        "message": f"₹{amount} dispensed successfully",
        "balance_after": new_balance,
        "transaction_id": str(txn.get("_id", ""))
    }), 200

@transactions_bp.route("/mini-statement", methods=["GET"])
@jwt_required()
def mini_statement():
    user_id = get_jwt_identity()
    txns = list(transactions_col.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).limit(5))
    return jsonify({"transactions": txns}), 200

@transactions_bp.route("/all", methods=["GET"])
@jwt_required()
def all_transactions():
    """Admin: get all transactions for anomaly analysis"""
    txns = list(transactions_col.find({}, {"_id": 0}).sort("timestamp", -1).limit(100))
    return jsonify({"transactions": txns}), 200
