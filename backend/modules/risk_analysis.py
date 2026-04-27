"""
Risk Analysis Module - STRIDE threat model scoring and mitigation suggestions
"""
from flask import Blueprint, jsonify
from modules.db import vulnerabilities_col, logs_col
from datetime import datetime

risk_bp = Blueprint("risk", __name__)

STRIDE_FULL = {
    "S": "Spoofing",
    "T": "Tampering",
    "R": "Repudiation",
    "I": "Information Disclosure",
    "D": "Denial of Service",
    "E": "Elevation of Privilege"
}

STRIDE_MITIGATIONS = {
    "S": [
        "Implement multi-factor authentication (MFA)",
        "Use digital certificates for ATM identity verification",
        "Deploy mutual TLS (mTLS) between ATM and server"
    ],
    "T": [
        "Enable data integrity checks (HMAC/digital signatures)",
        "Use AES-256 encryption for all stored data",
        "Implement database audit trails"
    ],
    "R": [
        "Enable comprehensive audit logging",
        "Use non-repudiation mechanisms (digital signatures on transactions)",
        "Store logs in tamper-proof storage (WORM)"
    ],
    "I": [
        "Enforce TLS 1.3 for all communications",
        "Encrypt sensitive fields (card number, PIN) with AES-256",
        "Apply data masking in logs and UI"
    ],
    "D": [
        "Implement rate limiting on all APIs",
        "Deploy DDoS protection (WAF, CDN)",
        "Configure connection timeouts and circuit breakers"
    ],
    "E": [
        "Apply principle of least privilege",
        "Separate ATM network from corporate network (VLAN)",
        "Regular privilege access reviews"
    ]
}

@risk_bp.route("/stride-analysis", methods=["GET"])
def stride_analysis():
    vulns = list(vulnerabilities_col.find({}, {"_id": 0}))

    stride_counts = {"S": 0, "T": 0, "R": 0, "I": 0, "D": 0, "E": 0}
    risk_counts = {"High": 0, "Medium": 0, "Low": 0}

    for v in vulns:
        stride_key = v.get("stride", "I")
        risk_level = v.get("risk", "Low")
        if stride_key in stride_counts:
            stride_counts[stride_key] += 1
        if risk_level in risk_counts:
            risk_counts[risk_level] += 1

    # Risk score: High=10, Medium=5, Low=1
    risk_score = (risk_counts["High"] * 10) + (risk_counts["Medium"] * 5) + (risk_counts["Low"] * 1)
    max_score = len(vulns) * 10 if vulns else 1
    risk_percentage = min(round((risk_score / max_score) * 100), 100)

    if risk_percentage >= 70:
        overall_risk = "Critical"
    elif risk_percentage >= 40:
        overall_risk = "High"
    elif risk_percentage >= 20:
        overall_risk = "Medium"
    else:
        overall_risk = "Low"

    stride_breakdown = []
    for key, count in stride_counts.items():
        if count > 0:
            stride_breakdown.append({
                "code": key,
                "name": STRIDE_FULL[key],
                "count": count,
                "mitigations": STRIDE_MITIGATIONS[key]
            })

    return jsonify({
        "stride_breakdown": stride_breakdown,
        "risk_counts": risk_counts,
        "risk_score": risk_score,
        "risk_percentage": risk_percentage,
        "overall_risk": overall_risk,
        "total_vulnerabilities": len(vulns),
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@risk_bp.route("/audit-logs", methods=["GET"])
def get_audit_logs():
    logs = list(logs_col.find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
    return jsonify({"logs": logs}), 200

@risk_bp.route("/security-recommendations", methods=["GET"])
def security_recommendations():
    recommendations = [
        {
            "category": "Encryption",
            "priority": "Critical",
            "items": [
                "Upgrade all ATM-to-server communication to TLS 1.3",
                "Encrypt PIN blocks using Triple-DES or AES-256 before transmission",
                "Use HSM (Hardware Security Module) for key management"
            ]
        },
        {
            "category": "Network Segmentation",
            "priority": "High",
            "items": [
                "Place ATMs in dedicated VLAN isolated from corporate network",
                "Deploy firewall rules: ATM can only reach payment processor IPs",
                "Disable all unused ports on ATM network switches"
            ]
        },
        {
            "category": "Authentication",
            "priority": "High",
            "items": [
                "Implement EMV chip verification alongside PIN",
                "Add behavioral biometrics for anomaly detection",
                "Lock card after 3 failed PIN attempts (already implemented)"
            ]
        },
        {
            "category": "Monitoring & Logging",
            "priority": "Medium",
            "items": [
                "Deploy SIEM (Security Information and Event Management)",
                "Set up real-time alerts for suspicious transactions",
                "Retain audit logs for minimum 7 years (PCI-DSS requirement)"
            ]
        },
        {
            "category": "Secure OS",
            "priority": "Medium",
            "items": [
                "Harden ATM OS: disable USB ports, CD drives",
                "Use application whitelisting on ATM terminals",
                "Apply OS patches within 30 days of release"
            ]
        }
    ]
    return jsonify({"recommendations": recommendations}), 200
