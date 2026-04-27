"""
Authentication module - Card insert, PIN verification, JWT issuance
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from modules.db import users_col, logs_col
import bcrypt
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

def log_event(event_type, user_id, details, ip="unknown"):
    logs_col.insert_one({
        "event_type": event_type,
        "user_id": user_id,
        "details": details,
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat()
    })

@auth_bp.route("/insert-card", methods=["POST"])
def insert_card():
    """Step 1: Validate card number exists"""
    data = request.json
    card_number = data.get("card_number", "").strip()

    if not card_number or len(card_number) != 16:
        return jsonify({"error": "Invalid card number"}), 400

    user = users_col.find_one({"card_number": card_number})
    if not user:
        log_event("CARD_NOT_FOUND", card_number, "Card not found in system", request.remote_addr)
        return jsonify({"error": "Card not recognized"}), 404

    if user.get("blocked"):
        log_event("BLOCKED_CARD", card_number, "Blocked card attempted", request.remote_addr)
        return jsonify({"error": "Card is blocked. Contact your bank."}), 403

    log_event("CARD_INSERTED", str(user["_id"]), "Card inserted successfully", request.remote_addr)
    return jsonify({"message": "Card accepted", "card_holder": user["name"]}), 200

@auth_bp.route("/verify-pin", methods=["POST"])
def verify_pin():
    """Step 2: Verify PIN and issue JWT"""
    data = request.json
    card_number = data.get("card_number", "").strip()
    pin = data.get("pin", "").strip()

    if not card_number or not pin:
        return jsonify({"error": "Card number and PIN required"}), 400

    user = users_col.find_one({"card_number": card_number})
    if not user:
        return jsonify({"error": "Card not found"}), 404

    # Check failed attempts
    failed_attempts = user.get("failed_attempts", 0)
    if failed_attempts >= 3:
        users_col.update_one({"card_number": card_number}, {"$set": {"blocked": True}})
        log_event("CARD_BLOCKED", card_number, "Card blocked after 3 failed PIN attempts", request.remote_addr)
        return jsonify({"error": "Card blocked after 3 failed attempts"}), 403

    # Verify PIN (bcrypt)
    if not bcrypt.checkpw(pin.encode(), user["pin_hash"].encode()):
        users_col.update_one({"card_number": card_number}, {"$inc": {"failed_attempts": 1}})
        remaining = 2 - failed_attempts
        log_event("WRONG_PIN", card_number, f"Wrong PIN. {remaining} attempts left", request.remote_addr)
        return jsonify({"error": f"Wrong PIN. {remaining} attempts remaining"}), 401

    # Reset failed attempts on success
    users_col.update_one({"card_number": card_number}, {"$set": {"failed_attempts": 0}})
    token = create_access_token(identity=str(user["_id"]))
    log_event("LOGIN_SUCCESS", str(user["_id"]), "PIN verified, session started", request.remote_addr)

    return jsonify({
        "token": token,
        "user_id": str(user["_id"]),
        "name": user["name"],
        "balance": user["balance"]
    }), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    log_event("LOGOUT", user_id, "User logged out", request.remote_addr)
    return jsonify({"message": "Session ended"}), 200
