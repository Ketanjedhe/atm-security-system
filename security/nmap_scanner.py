"""
Standalone Nmap Scanner Script
Usage: python security/nmap_scanner.py --target 192.168.1.1 --ports 1-1024
"""
import argparse
import json
from datetime import datetime

STRIDE_MAP = {
    "21":   {"service": "FTP",     "threat": "Spoofing",             "stride": "S", "risk": "High"},
    "22":   {"service": "SSH",     "threat": "Brute Force",          "stride": "S", "risk": "Medium"},
    "23":   {"service": "Telnet",  "threat": "Info Disclosure",      "stride": "I", "risk": "High"},
    "80":   {"service": "HTTP",    "threat": "Tampering / MitM",     "stride": "T", "risk": "High"},
    "443":  {"service": "HTTPS",   "threat": "Weak TLS Config",      "stride": "I", "risk": "Medium"},
    "3306": {"service": "MySQL",   "threat": "Privilege Escalation", "stride": "E", "risk": "High"},
    "27017":{"service": "MongoDB", "threat": "Unauth DB Access",     "stride": "E", "risk": "High"},
    "8080": {"service": "HTTP-Alt","threat": "Repudiation",          "stride": "R", "risk": "Medium"},
    "5000": {"service": "Flask",   "threat": "DoS / API Abuse",      "stride": "D", "risk": "Medium"},
}

def scan(target, ports="1-1024"):
    print(f"\n[*] Starting Nmap scan on {target} (ports {ports})")
    try:
        import nmap
        nm = nmap.PortScanner()
        nm.scan(hosts=target, arguments=f"-p {ports} -sV --open -T4")
        open_ports = []
        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                for port in nm[host][proto].keys():
                    if nm[host][proto][port]["state"] == "open":
                        open_ports.append(str(port))
        print(f"[+] Nmap scan complete. Open ports: {open_ports}")
        return open_ports, "nmap"
    except ImportError:
        print("[!] python-nmap not installed. Using simulated data.")
        return ["22", "80", "443", "3306", "8080", "5000"], "simulated"
    except Exception as e:
        print(f"[!] Nmap error: {e}. Using simulated data.")
        return ["22", "80", "443", "3306", "8080", "5000"], "simulated"

def analyze(open_ports):
    print("\n[*] Analyzing vulnerabilities using STRIDE model...\n")
    results = []
    for port in open_ports:
        if port in STRIDE_MAP:
            v = STRIDE_MAP[port].copy()
            v["port"] = port
            results.append(v)
            risk_color = "\033[91m" if v["risk"] == "High" else "\033[93m" if v["risk"] == "Medium" else "\033[92m"
            reset = "\033[0m"
            print(f"  Port {port:>5} | {v['service']:<10} | {v['threat']:<30} | STRIDE: {v['stride']} | Risk: {risk_color}{v['risk']}{reset}")
    return results

def main():
    parser = argparse.ArgumentParser(description="ATM Network Nmap Security Scanner")
    parser.add_argument("--target", default="127.0.0.1", help="Target IP or hostname")
    parser.add_argument("--ports", default="1-1024", help="Port range to scan")
    parser.add_argument("--output", default=None, help="Save results to JSON file")
    args = parser.parse_args()

    open_ports, mode = scan(args.target, args.ports)
    vulns = analyze(open_ports)

    high = sum(1 for v in vulns if v["risk"] == "High")
    med  = sum(1 for v in vulns if v["risk"] == "Medium")
    low  = sum(1 for v in vulns if v["risk"] == "Low")

    print(f"\n[+] Summary: {len(open_ports)} open ports | High: {high} | Medium: {med} | Low: {low}")
    print(f"[+] Scan mode: {mode}")

    report = {
        "target": args.target,
        "scan_mode": mode,
        "timestamp": datetime.utcnow().isoformat(),
        "open_ports": open_ports,
        "vulnerabilities": vulns,
        "summary": {"total": len(vulns), "high": high, "medium": med, "low": low}
    }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"[+] Results saved to {args.output}")

if __name__ == "__main__":
    main()
