"""
Database seed script - Creates sample users, transactions, and vulnerability data
Run: python database/seed.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.db import users_col, transactions_col, vulnerabilities_col, logs_col
import bcrypt
from datetime import datetime, timedelta
import random

def hash_pin(pin: str) -> str:
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()

def seed():
    print("Clearing existing data...")
    users_col.delete_many({})
    transactions_col.delete_many({})
    vulnerabilities_col.delete_many({})
    logs_col.delete_many({})

    # --- USERS ---
    users = [
        {
            "name": "Rahul Sharma",
            "card_number": "4111111111111111",
            "pin_hash": hash_pin("1234"),
            "balance": 50000.0,
            "account_number": "SBI001234567",
            "failed_attempts": 0,
            "blocked": False,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Priya Patel",
            "card_number": "5500005555555559",
            "pin_hash": hash_pin("5678"),
            "balance": 25000.0,
            "account_number": "HDFC009876543",
            "failed_attempts": 0,
            "blocked": False,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Amit Kumar",
            "card_number": "3714496353984312",
            "pin_hash": hash_pin("9999"),
            "balance": 10000.0,
            "account_number": "ICICI005432198",
            "failed_attempts": 0,
            "blocked": False,
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    users_col.insert_many(users)
    print(f"Inserted {len(users)} users")

    # --- TRANSACTIONS ---
    user_ids = ["user_001", "user_002", "user_003"]
    txns = []
    base_time = datetime.utcnow() - timedelta(days=30)
    amounts = [500, 1000, 1500, 2000, 3000, 500, 800, 1200, 700, 900]
    for i, amount in enumerate(amounts):
        txns.append({
            "user_id": random.choice(user_ids),
            "type": "WITHDRAWAL",
            "amount": amount,
            "balance_after": 50000 - sum(amounts[:i+1]),
            "timestamp": (base_time + timedelta(days=i*2, hours=random.randint(9, 18))).isoformat(),
            "status": "SUCCESS"
        })
    # Add suspicious transactions
    txns.append({
        "user_id": "user_001",
        "type": "WITHDRAWAL",
        "amount": 19900,
        "balance_after": 100,
        "timestamp": (datetime.utcnow() - timedelta(hours=2)).replace(hour=3).isoformat(),
        "status": "SUCCESS"
    })
    transactions_col.insert_many(txns)
    print(f"Inserted {len(txns)} transactions")

    # --- VULNERABILITIES ---
    vulns = [
        {"port": "23",   "service": "Telnet",  "threat": "Info Disclosure",      "stride": "I", "risk": "High",   "mitigation": "Disable Telnet, use SSH", "scan_target": "127.0.0.1"},
        {"port": "80",   "service": "HTTP",    "threat": "Tampering / MitM",     "stride": "T", "risk": "High",   "mitigation": "Redirect to HTTPS, enforce HSTS", "scan_target": "127.0.0.1"},
        {"port": "3306", "service": "MySQL",   "threat": "Privilege Escalation", "stride": "E", "risk": "High",   "mitigation": "Restrict MySQL to localhost, change default creds", "scan_target": "127.0.0.1"},
        {"port": "22",   "service": "SSH",     "threat": "Brute Force",          "stride": "S", "risk": "Medium", "mitigation": "Use key-based auth, disable password login", "scan_target": "127.0.0.1"},
        {"port": "8080", "service": "HTTP-Alt","threat": "Repudiation",          "stride": "R", "risk": "Medium", "mitigation": "Enable access logging, require auth", "scan_target": "127.0.0.1"},
        {"port": "5000", "service": "Flask",   "threat": "DoS / API Abuse",      "stride": "D", "risk": "Medium", "mitigation": "Add rate limiting, deploy behind nginx", "scan_target": "127.0.0.1"},
    ]
    for v in vulns:
        v["timestamp"] = datetime.utcnow().isoformat()
    vulnerabilities_col.insert_many(vulns)
    print(f"Inserted {len(vulns)} vulnerabilities")

    # --- AUDIT LOGS ---
    log_events = [
        {"event_type": "CARD_INSERTED",   "user_id": "user_001", "details": "Card inserted successfully", "ip": "192.168.1.10"},
        {"event_type": "LOGIN_SUCCESS",   "user_id": "user_001", "details": "PIN verified", "ip": "192.168.1.10"},
        {"event_type": "WITHDRAWAL",      "user_id": "user_001", "details": "Withdrew ₹1000", "ip": "192.168.1.10"},
        {"event_type": "WRONG_PIN",       "user_id": "user_002", "details": "Wrong PIN. 2 attempts left", "ip": "192.168.1.15"},
        {"event_type": "CARD_BLOCKED",    "user_id": "user_003", "details": "Card blocked after 3 failed attempts", "ip": "10.0.0.99"},
        {"event_type": "BALANCE_CHECK",   "user_id": "user_002", "details": "Balance enquiry", "ip": "192.168.1.15"},
        {"event_type": "LOGOUT",          "user_id": "user_001", "details": "Session ended", "ip": "192.168.1.10"},
    ]
    for log in log_events:
        log["timestamp"] = datetime.utcnow().isoformat()
    logs_col.insert_many(log_events)
    print(f"Inserted {len(log_events)} audit logs")

    print("\nSeed complete. Test credentials:")
    print("  Card: 4111111111111111  PIN: 1234  (Rahul Sharma)")
    print("  Card: 5500005555555559  PIN: 5678  (Priya Patel)")
    print("  Card: 3714496353984312  PIN: 9999  (Amit Kumar)")

if __name__ == "__main__":
    seed()
