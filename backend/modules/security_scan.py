"""
Security Scan Module - Nmap port scanning + simulated vulnerability detection
Integrates with: Nmap, simulated Wireshark/Metasploit findings
"""
from flask import Blueprint, request, jsonify
from modules.db import scan_results_col, vulnerabilities_col
from datetime import datetime
import subprocess
import json

security_bp = Blueprint("security", __name__)

# STRIDE threat categories
STRIDE_MAP = {
    "21":  {"service": "FTP",    "threat": "Spoofing",              "stride": "S", "risk": "High"},
    "22":  {"service": "SSH",    "threat": "Brute Force",           "stride": "S", "risk": "Medium"},
    "23":  {"service": "Telnet", "threat": "Info Disclosure",       "stride": "I", "risk": "High"},
    "80":  {"service": "HTTP",   "threat": "Tampering / MitM",      "stride": "T", "risk": "High"},
    "443": {"service": "HTTPS",  "threat": "Weak TLS Config",       "stride": "I", "risk": "Medium"},
    "3306":{"service": "MySQL",  "threat": "Privilege Escalation",  "stride": "E", "risk": "High"},
    "27017":{"service":"MongoDB","threat": "Unauth DB Access",      "stride": "E", "risk": "High"},
    "8080":{"service": "HTTP-Alt","threat":"Repudiation / No Logs", "stride": "R", "risk": "Medium"},
    "5000":{"service": "Flask",  "threat": "DoS / API Abuse",       "stride": "D", "risk": "Medium"},
}

MITIGATIONS = {
    "High":   "Immediately patch, restrict access, apply firewall rules",
    "Medium": "Schedule patch, monitor traffic, enable logging",
    "Low":    "Document and review in next security cycle"
}

def try_nmap_scan(target, ports="1-1024"):
    """Try real nmap scan, fall back to simulation if nmap not installed"""
    try:
        import nmap
        nm = nmap.PortScanner()
        nm.scan(hosts=target, arguments=f"-p {ports} -sV --open -T4")
        open_ports = []
        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                for port in nm[host][proto].keys():
                    state = nm[host][proto][port]["state"]
                    if state == "open":
                        open_ports.append(str(port))
        return open_ports, "nmap"
    except Exception:
        # Simulate realistic ATM network ports when nmap unavailable
        simulated = ["22", "80", "443", "3306", "8080", "5000"]
        return simulated, "simulated"

@security_bp.route("/scan", methods=["POST"])
def run_scan():
    data = request.json or {}
    target = data.get("target", "127.0.0.1")
    ports = data.get("ports", "1-1024")

    open_ports, scan_mode = try_nmap_scan(target, ports)

    vulnerabilities = []
    for port in open_ports:
        if port in STRIDE_MAP:
            entry = STRIDE_MAP[port].copy()
            entry["port"] = port
            entry["mitigation"] = MITIGATIONS[entry["risk"]]
            vulnerabilities.append(entry)
        else:
            vulnerabilities.append({
                "port": port,
                "service": "Unknown",
                "threat": "Unknown Service Exposure",
                "stride": "I",
                "risk": "Low",
                "mitigation": MITIGATIONS["Low"]
            })

    result = {
        "target": target,
        "scan_mode": scan_mode,
        "open_ports": open_ports,
        "vulnerabilities": vulnerabilities,
        "total_open": len(open_ports),
        "high_risk": sum(1 for v in vulnerabilities if v["risk"] == "High"),
        "medium_risk": sum(1 for v in vulnerabilities if v["risk"] == "Medium"),
        "low_risk": sum(1 for v in vulnerabilities if v["risk"] == "Low"),
        "timestamp": datetime.utcnow().isoformat()
    }

    scan_results_col.insert_one({**result})
    # Also store each vuln
    for v in vulnerabilities:
        v["scan_target"] = target
        v["timestamp"] = result["timestamp"]
        vulnerabilities_col.update_one(
            {"port": v["port"], "scan_target": target},
            {"$set": v},
            upsert=True
        )

    result.pop("_id", None)
    return jsonify(result), 200

@security_bp.route("/vulnerabilities", methods=["GET"])
def get_vulnerabilities():
    vulns = list(vulnerabilities_col.find({}, {"_id": 0}).sort("timestamp", -1))
    return jsonify({"vulnerabilities": vulns}), 200

@security_bp.route("/wireshark-simulation", methods=["GET"])
def wireshark_simulation():
    """
    Simulates Wireshark packet capture findings.
    In real deployment: run tshark -i eth0 -w capture.pcap and parse output.
    """
    simulated_packets = [
        {"no": 1, "time": "0.000", "src": "192.168.1.10", "dst": "192.168.1.1",
         "protocol": "TCP", "info": "SYN - ATM client initiating connection", "risk": "Low"},
        {"no": 2, "time": "0.001", "src": "192.168.1.1",  "dst": "192.168.1.10",
         "protocol": "TCP", "info": "SYN-ACK - Server responding", "risk": "Low"},
        {"no": 3, "time": "0.050", "src": "192.168.1.10", "dst": "192.168.1.1",
         "protocol": "TLS", "info": "Client Hello - TLS 1.2 handshake", "risk": "Medium"},
        {"no": 4, "time": "0.100", "src": "192.168.1.99", "dst": "192.168.1.1",
         "protocol": "ARP",  "info": "ARP Spoofing detected - MAC mismatch", "risk": "High"},
        {"no": 5, "time": "0.200", "src": "192.168.1.10", "dst": "192.168.1.1",
         "protocol": "HTTP", "info": "Unencrypted PIN data in HTTP request", "risk": "High"},
        {"no": 6, "time": "0.300", "src": "10.0.0.5",     "dst": "192.168.1.1",
         "protocol": "TCP",  "info": "Port scan detected from external IP", "risk": "High"},
    ]
    return jsonify({"packets": simulated_packets, "note": "Simulated Wireshark capture"}), 200

@security_bp.route("/metasploit-simulation", methods=["GET"])
def metasploit_simulation():
    """
    Simulates Metasploit attack scenarios against ATM network.
    In real deployment: use msfrpc client to run modules programmatically.
    """
    scenarios = [
        {
            "module": "auxiliary/scanner/portscan/tcp",
            "target": "192.168.1.0/24",
            "result": "Open ports: 22, 80, 3306, 5000",
            "risk": "Medium",
            "description": "TCP port scan reveals exposed services"
        },
        {
            "module": "exploit/multi/handler",
            "target": "192.168.1.10:80",
            "result": "HTTP service running without authentication",
            "risk": "High",
            "description": "Unprotected admin endpoint accessible"
        },
        {
            "module": "auxiliary/scanner/mysql/mysql_login",
            "target": "192.168.1.10:3306",
            "result": "Default credentials accepted: root/root",
            "risk": "High",
            "description": "MySQL using default credentials - critical vulnerability"
        },
        {
            "module": "auxiliary/dos/tcp/synflood",
            "target": "192.168.1.10",
            "result": "ATM service unresponsive after 500 SYN packets",
            "risk": "High",
            "description": "SYN flood DoS attack successful - no rate limiting"
        }
    ]
    return jsonify({"scenarios": scenarios, "note": "Simulated Metasploit attack scenarios"}), 200

@security_bp.route("/burp-simulation", methods=["GET"])
def burp_simulation():
    """
    Simulates Burp Suite / OWASP ZAP API security test findings.
    """
    findings = [
        {"id": 1, "type": "SQL Injection",        "endpoint": "/api/auth/verify-pin",
         "severity": "High",   "detail": "PIN parameter not sanitized"},
        {"id": 2, "type": "Missing HTTPS",         "endpoint": "/api/transactions/withdraw",
         "severity": "High",   "detail": "Transaction API accessible over HTTP"},
        {"id": 3, "type": "JWT None Algorithm",    "endpoint": "/api/auth/verify-pin",
         "severity": "High",   "detail": "JWT accepts 'none' algorithm"},
        {"id": 4, "type": "CORS Misconfiguration", "endpoint": "/api/*",
         "severity": "Medium", "detail": "Wildcard CORS origin allowed"},
        {"id": 5, "type": "Rate Limiting Missing", "endpoint": "/api/auth/verify-pin",
         "severity": "Medium", "detail": "No brute-force protection on PIN endpoint"},
        {"id": 6, "type": "Verbose Error Messages","endpoint": "/api/auth/insert-card",
         "severity": "Low",    "detail": "Stack traces exposed in error responses"},
    ]
    return jsonify({"findings": findings, "note": "Simulated Burp Suite / OWASP ZAP scan"}), 200
