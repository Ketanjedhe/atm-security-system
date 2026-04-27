# ATM Network Security Audit & Cybersecurity Risk Analysis System
### B.Tech Final Year Project

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ATM CLIENT (React)                       │
│  Card Insert → PIN Entry → Menu → Withdraw / Statement       │
│  Security Dashboard → Vulnerability View → Anomaly Detection │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS / JWT
┌──────────────────────▼──────────────────────────────────────┐
│                  BACKEND SERVER (Flask)                       │
│  /api/auth        → Card + PIN authentication                │
│  /api/transactions → Withdraw, Balance, Statement            │
│  /api/security    → Nmap scan, Wireshark/Metasploit/Burp sim │
│  /api/risk        → STRIDE analysis, Audit logs, Recs        │
│  /api/anomaly     → Isolation Forest ML detection            │
│  /api/reports     → PDF report generation                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   DATABASE (MongoDB)                          │
│  users · transactions · audit_logs · vulnerabilities         │
│  scan_results                                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack
- Frontend: React 18, React Router, Recharts, Axios
- Backend: Flask 3, Flask-JWT-Extended, Flask-CORS
- Database: MongoDB (via PyMongo)
- Security: python-nmap, bcrypt, cryptography
- ML: scikit-learn (Isolation Forest)
- Reports: ReportLab (PDF)

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (running on localhost:27017)
- Nmap installed (optional, falls back to simulation)

---

### Step 1: Backend Setup

```bash
cd atm-security-system/backend
pip install -r requirements.txt
```

### Step 2: Seed the Database

```bash
cd atm-security-system
python database/seed.py
```

### Step 3: Start Backend

```bash
cd atm-security-system/backend
python app.py
```
Backend runs at: http://localhost:5000

### Step 4: Frontend Setup

```bash
cd atm-security-system/frontend
npm install
npm start
```
Frontend runs at: http://localhost:3000

---

## Test Credentials

| Card Number      | PIN  | Name         | Balance  |
|-----------------|------|--------------|----------|
| 4111111111111111 | 1234 | Rahul Sharma | ₹50,000  |
| 5500005555555559 | 5678 | Priya Patel  | ₹25,000  |
| 3714496353984312 | 9999 | Amit Kumar   | ₹10,000  |

---

## Security Tools Integration

### Nmap (Real scan if installed)
```bash
python security/nmap_scanner.py --target 127.0.0.1 --ports 1-1024 --output results.json
```

### Anomaly Detection (Standalone)
```bash
python security/anomaly_standalone.py
```

### PDF Report
Visit: http://localhost:5000/api/reports/generate-pdf

---

## API Endpoints

| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| POST   | /api/auth/insert-card             | Validate card            |
| POST   | /api/auth/verify-pin              | Verify PIN, get JWT      |
| GET    | /api/transactions/balance         | Get balance              |
| POST   | /api/transactions/withdraw        | Withdraw cash            |
| GET    | /api/transactions/mini-statement  | Last 5 transactions      |
| POST   | /api/security/scan                | Run Nmap scan            |
| GET    | /api/security/vulnerabilities     | Get all vulnerabilities  |
| GET    | /api/security/wireshark-simulation| Wireshark packet data    |
| GET    | /api/security/metasploit-simulation| Metasploit scenarios    |
| GET    | /api/security/burp-simulation     | Burp/ZAP findings        |
| GET    | /api/risk/stride-analysis         | STRIDE threat analysis   |
| GET    | /api/risk/audit-logs              | Audit event logs         |
| GET    | /api/risk/security-recommendations| Security recommendations |
| POST   | /api/anomaly/detect               | Detect single anomaly    |
| GET    | /api/anomaly/analyze-all          | Analyze all transactions |
| GET    | /api/reports/generate-pdf         | Download PDF report      |

---

## STRIDE Threat Model

| Letter | Threat                | ATM Example                        |
|--------|-----------------------|------------------------------------|
| S      | Spoofing              | Fake ATM card / skimming           |
| T      | Tampering             | Modifying transaction data         |
| R      | Repudiation           | Denying a withdrawal was made      |
| I      | Information Disclosure| PIN captured over unencrypted link |
| D      | Denial of Service     | SYN flood on ATM network           |
| E      | Elevation of Privilege| Accessing admin panel via SQL inj  |

---

## Security Features Implemented
- bcrypt PIN hashing
- JWT session tokens
- Card blocking after 3 failed PIN attempts
- Full audit logging of all events
- Isolation Forest anomaly detection
- STRIDE-mapped vulnerability analysis
- PDF security audit report generation
