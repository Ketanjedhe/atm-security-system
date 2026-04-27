import React, { useState, useEffect } from "react";
import api from "../api/client";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";

const COLORS = { High: "#ff1744", Medium: "#ff9100", Low: "#00c853", Normal: "#00c853", Critical: "#d50000" };
const PIE_COLORS = ["#ff1744", "#ff9100", "#00c853"];

const s = {
  page: { maxWidth: 1100, margin: "0 auto", padding: "32px 20px" },
  title: { fontSize: 26, fontWeight: 800, color: "#4f8ef7", marginBottom: 6 },
  sub: { color: "#6b7a99", fontSize: 14, marginBottom: 28 },
  tabs: { display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" },
  tab: (active) => ({
    background: active ? "#4f8ef7" : "#1a2540",
    color: active ? "#fff" : "#a0b0cc",
    border: `1px solid ${active ? "#4f8ef7" : "#2a3a5c"}`,
    padding: "8px 18px", borderRadius: 20, fontSize: 13, fontWeight: 600
  }),
  grid2: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 24 },
  grid3: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16, marginBottom: 24 },
  card: {
    background: "#111827", border: "1px solid #1e2d4a",
    borderRadius: 12, padding: 20
  },
  statNum: { fontSize: 36, fontWeight: 800, marginBottom: 4 },
  statLabel: { color: "#6b7a99", fontSize: 13 },
  scanBtn: { background: "#4f8ef7", color: "#fff", padding: "10px 24px", marginBottom: 20 },
  reportBtn: { background: "#7c3aed", color: "#fff", padding: "10px 24px", marginBottom: 20, marginLeft: 10 },
  table: { width: "100%", borderCollapse: "collapse", fontSize: 13 },
  th: { background: "#0d1526", color: "#a0b0cc", padding: "10px 12px", textAlign: "left", borderBottom: "1px solid #1e2d4a" },
  td: { padding: "10px 12px", borderBottom: "1px solid #1a2540", color: "#c0cce0" },
  badge: (risk) => ({
    display: "inline-block", padding: "2px 10px", borderRadius: 20,
    fontSize: 11, fontWeight: 700,
    background: COLORS[risk] || "#4a5568", color: "#fff"
  }),
  sectionTitle: { fontSize: 16, fontWeight: 700, color: "#a0b0cc", marginBottom: 14 },
  anomalyForm: { display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 16 },
  anomalyInput: { flex: 1, minWidth: 140 },
  anomalyBtn: { background: "#059669", color: "#fff", padding: "10px 20px" },
  resultBox: (isAnomaly) => ({
    background: isAnomaly ? "#2a0a0a" : "#0a2a1a",
    border: `1px solid ${isAnomaly ? "#ff1744" : "#00c853"}`,
    borderRadius: 10, padding: 20, marginTop: 16
  }),
  logRow: (i) => ({
    padding: "8px 12px",
    background: i % 2 === 0 ? "#0d1526" : "#111827",
    borderRadius: 6, marginBottom: 4, fontSize: 12,
    display: "flex", justifyContent: "space-between", gap: 10
  }),
  recCard: {
    background: "#0d1526", border: "1px solid #1e2d4a",
    borderRadius: 10, padding: 16, marginBottom: 12
  },
  recTitle: { fontWeight: 700, color: "#4f8ef7", marginBottom: 8 },
  recItem: { color: "#a0b0cc", fontSize: 13, marginBottom: 4 }
};

const TABS = ["Overview", "Vulnerabilities", "STRIDE", "Anomaly Detection", "Audit Logs", "Tools", "Recommendations"];

export default function Dashboard() {
  const [tab, setTab] = useState("Overview");
  const [vulns, setVulns] = useState([]);
  const [stride, setStride] = useState(null);
  const [logs, setLogs] = useState([]);
  const [recs, setRecs] = useState([]);
  const [wireshark, setWireshark] = useState(null);
  const [metasploit, setMetasploit] = useState(null);
  const [burp, setBurp] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [scanTarget, setScanTarget] = useState("127.0.0.1");
  const [anomalyInput, setAnomalyInput] = useState({ amount: "", timestamp: "", type: "WITHDRAWAL" });
  const [anomalyResult, setAnomalyResult] = useState(null);
  const [anomalyLoading, setAnomalyLoading] = useState(false);

  useEffect(() => {
    api.get("/security/vulnerabilities").then(r => setVulns(r.data.vulnerabilities)).catch(() => {});
    api.get("/risk/stride-analysis").then(r => setStride(r.data)).catch(() => {});
    api.get("/risk/audit-logs").then(r => setLogs(r.data.logs)).catch(() => {});
    api.get("/risk/security-recommendations").then(r => setRecs(r.data.recommendations)).catch(() => {});
  }, []);

  const runScan = async () => {
    setScanning(true);
    try {
      const res = await api.post("/security/scan", { target: scanTarget });
      setVulns(res.data.vulnerabilities);
      const strideRes = await api.get("/risk/stride-analysis");
      setStride(strideRes.data);
    } catch (e) {
      alert("Scan failed: " + (e.response?.data?.error || e.message));
    } finally {
      setScanning(false);
    }
  };

  const loadTool = async (tool) => {
    try {
      if (tool === "wireshark") {
        const r = await api.get("/security/wireshark-simulation");
        setWireshark(r.data);
      } else if (tool === "metasploit") {
        const r = await api.get("/security/metasploit-simulation");
        setMetasploit(r.data);
      } else if (tool === "burp") {
        const r = await api.get("/security/burp-simulation");
        setBurp(r.data);
      }
    } catch (e) { alert("Failed to load tool data"); }
  };

  const detectAnomaly = async () => {
    if (!anomalyInput.amount) return;
    setAnomalyLoading(true);
    try {
      const res = await api.post("/anomaly/detect", {
        amount: parseFloat(anomalyInput.amount),
        timestamp: anomalyInput.timestamp || new Date().toISOString(),
        type: anomalyInput.type
      });
      setAnomalyResult(res.data);
    } catch (e) {
      alert("Detection failed");
    } finally {
      setAnomalyLoading(false);
    }
  };

  const downloadReport = () => {
    window.open("http://localhost:5000/api/reports/generate-pdf", "_blank");
  };

  const high = vulns.filter(v => v.risk === "High").length;
  const med  = vulns.filter(v => v.risk === "Medium").length;
  const low  = vulns.filter(v => v.risk === "Low").length;
  const pieData = [
    { name: "High", value: high },
    { name: "Medium", value: med },
    { name: "Low", value: low }
  ].filter(d => d.value > 0);

  return (
    <div style={s.page}>
      <div style={s.title}>🛡️ Security Audit Dashboard</div>
      <div style={s.sub}>ATM Network Cybersecurity Risk Analysis — STRIDE Threat Model</div>

      <div style={s.tabs}>
        {TABS.map(t => (
          <button key={t} style={s.tab(tab === t)} onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>

      {/* OVERVIEW */}
      {tab === "Overview" && (
        <>
          <div style={s.grid3}>
            <div style={s.card}>
              <div style={{...s.statNum, color: "#ff1744"}}>{high}</div>
              <div style={s.statLabel}>High Risk Vulnerabilities</div>
            </div>
            <div style={s.card}>
              <div style={{...s.statNum, color: "#ff9100"}}>{med}</div>
              <div style={s.statLabel}>Medium Risk</div>
            </div>
            <div style={s.card}>
              <div style={{...s.statNum, color: "#00c853"}}>{low}</div>
              <div style={s.statLabel}>Low Risk</div>
            </div>
          </div>
          {stride && (
            <div style={s.grid2}>
              <div style={s.card}>
                <div style={s.sectionTitle}>Risk Distribution</div>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label>
                      {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                    </Pie>
                    <Legend />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div style={s.card}>
                <div style={s.sectionTitle}>Overall Risk Score</div>
                <div style={{...s.statNum, color: COLORS[stride.overall_risk] || "#4f8ef7", fontSize: 48}}>
                  {stride.risk_percentage}%
                </div>
                <div style={{...s.badge(stride.overall_risk), fontSize: 14, padding: "4px 16px"}}>
                  {stride.overall_risk} Risk
                </div>
                <div style={{color: "#6b7a99", fontSize: 13, marginTop: 12}}>
                  {stride.total_vulnerabilities} total vulnerabilities detected
                </div>
              </div>
            </div>
          )}
          <div style={s.card}>
            <div style={s.sectionTitle}>STRIDE Threat Breakdown</div>
            {stride && (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={stride.stride_breakdown}>
                  <XAxis dataKey="name" tick={{fill: "#a0b0cc", fontSize: 12}} />
                  <YAxis tick={{fill: "#a0b0cc", fontSize: 12}} />
                  <Tooltip contentStyle={{background: "#111827", border: "1px solid #1e2d4a"}} />
                  <Bar dataKey="count" fill="#4f8ef7" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </>
      )}

      {/* VULNERABILITIES */}
      {tab === "Vulnerabilities" && (
        <div style={s.card}>
          <div style={{display: "flex", alignItems: "center", gap: 10, marginBottom: 16, flexWrap: "wrap"}}>
            <input
              style={{width: 200}}
              value={scanTarget}
              onChange={e => setScanTarget(e.target.value)}
              placeholder="Target IP"
              aria-label="Scan target IP"
            />
            <button style={s.scanBtn} onClick={runScan} disabled={scanning}>
              {scanning ? "Scanning..." : "🔍 Run Nmap Scan"}
            </button>
            <button style={s.reportBtn} onClick={downloadReport}>
              📄 Download PDF Report
            </button>
          </div>
          <table style={s.table}>
            <thead>
              <tr>
                {["Port","Service","Threat","STRIDE","Risk","Mitigation"].map(h => (
                  <th key={h} style={s.th}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {vulns.map((v, i) => (
                <tr key={i}>
                  <td style={s.td}>{v.port}</td>
                  <td style={s.td}>{v.service}</td>
                  <td style={s.td}>{v.threat}</td>
                  <td style={s.td}>{v.stride}</td>
                  <td style={s.td}><span style={s.badge(v.risk)}>{v.risk}</span></td>
                  <td style={s.td}>{v.mitigation}</td>
                </tr>
              ))}
              {vulns.length === 0 && (
                <tr><td colSpan={6} style={{...s.td, textAlign: "center", color: "#4a5568"}}>
                  No vulnerabilities. Run a scan first.
                </td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* STRIDE */}
      {tab === "STRIDE" && stride && (
        <div>
          <div style={{...s.card, marginBottom: 20}}>
            <div style={s.sectionTitle}>STRIDE Threat Model Analysis</div>
            <table style={s.table}>
              <thead>
                <tr>
                  {["Category","Code","Count","Mitigations"].map(h => <th key={h} style={s.th}>{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {stride.stride_breakdown.map((item, i) => (
                  <tr key={i}>
                    <td style={s.td}>{item.name}</td>
                    <td style={s.td}>{item.code}</td>
                    <td style={s.td}>{item.count}</td>
                    <td style={s.td}>
                      <ul style={{paddingLeft: 16}}>
                        {item.mitigations.map((m, j) => <li key={j} style={{marginBottom: 4}}>{m}</li>)}
                      </ul>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ANOMALY DETECTION */}
      {tab === "Anomaly Detection" && (
        <div style={s.card}>
          <div style={s.sectionTitle}>🤖 ML Anomaly Detection (Isolation Forest)</div>
          <p style={{color: "#6b7a99", fontSize: 13, marginBottom: 16}}>
            Enter a transaction to check if it's suspicious. The model is trained on historical ATM transactions.
          </p>
          <div style={s.anomalyForm}>
            <div style={s.anomalyInput}>
              <label style={{color: "#a0b0cc", fontSize: 12, display: "block", marginBottom: 4}}>Amount (₹)</label>
              <input
                type="number"
                placeholder="e.g. 19900"
                value={anomalyInput.amount}
                onChange={e => setAnomalyInput({...anomalyInput, amount: e.target.value})}
                aria-label="Transaction amount"
              />
            </div>
            <div style={s.anomalyInput}>
              <label style={{color: "#a0b0cc", fontSize: 12, display: "block", marginBottom: 4}}>Timestamp</label>
              <input
                type="datetime-local"
                value={anomalyInput.timestamp}
                onChange={e => setAnomalyInput({...anomalyInput, timestamp: new Date(e.target.value).toISOString()})}
                aria-label="Transaction timestamp"
              />
            </div>
            <div style={{display: "flex", alignItems: "flex-end"}}>
              <button style={s.anomalyBtn} onClick={detectAnomaly} disabled={anomalyLoading || !anomalyInput.amount}>
                {anomalyLoading ? "Analyzing..." : "Detect Anomaly"}
              </button>
            </div>
          </div>
          {anomalyResult && (
            <div style={s.resultBox(anomalyResult.is_anomaly)}>
              <div style={{fontSize: 20, fontWeight: 700, color: anomalyResult.is_anomaly ? "#ff1744" : "#00e676", marginBottom: 8}}>
                {anomalyResult.is_anomaly ? "⚠️ ANOMALY DETECTED" : "✅ Transaction Normal"}
              </div>
              <div style={{color: "#a0b0cc", fontSize: 13, marginBottom: 8}}>
                Anomaly Score: {anomalyResult.anomaly_score} &nbsp;|&nbsp;
                Risk: <span style={s.badge(anomalyResult.risk_level)}>{anomalyResult.risk_level}</span>
              </div>
              <div style={{color: "#c0cce0", fontSize: 13}}>
                <strong>Reasons:</strong>
                <ul style={{paddingLeft: 16, marginTop: 4}}>
                  {anomalyResult.reasons.map((r, i) => <li key={i}>{r}</li>)}
                </ul>
              </div>
              <div style={{color: "#6b7a99", fontSize: 12, marginTop: 8}}>
                Recommendation: {anomalyResult.recommendation}
              </div>
            </div>
          )}
        </div>
      )}

      {/* AUDIT LOGS */}
      {tab === "Audit Logs" && (
        <div style={s.card}>
          <div style={s.sectionTitle}>📜 Audit Logs (Last 50 Events)</div>
          {logs.map((log, i) => (
            <div key={i} style={s.logRow(i)}>
              <span style={{color: "#4f8ef7", minWidth: 160}}>{log.event_type}</span>
              <span style={{color: "#a0b0cc", flex: 1}}>{log.details}</span>
              <span style={{color: "#4a5568", minWidth: 140, textAlign: "right"}}>
                {log.timestamp?.slice(0, 19).replace("T", " ")}
              </span>
            </div>
          ))}
          {logs.length === 0 && <div style={{color: "#4a5568", textAlign: "center", padding: 24}}>No logs yet</div>}
        </div>
      )}

      {/* TOOLS */}
      {tab === "Tools" && (
        <div>
          <div style={{display: "flex", gap: 10, marginBottom: 20, flexWrap: "wrap"}}>
            <button style={{...s.scanBtn, background: "#0d47a1"}} onClick={() => loadTool("wireshark")}>
              📡 Wireshark Simulation
            </button>
            <button style={{...s.scanBtn, background: "#b71c1c"}} onClick={() => loadTool("metasploit")}>
              💀 Metasploit Scenarios
            </button>
            <button style={{...s.scanBtn, background: "#e65100"}} onClick={() => loadTool("burp")}>
              🕷️ Burp/ZAP Findings
            </button>
          </div>

          {wireshark && (
            <div style={{...s.card, marginBottom: 20}}>
              <div style={s.sectionTitle}>📡 Wireshark Packet Capture (Simulated)</div>
              <p style={{color: "#4a5568", fontSize: 12, marginBottom: 12}}>{wireshark.note}</p>
              <table style={s.table}>
                <thead>
                  <tr>{["No","Time","Source","Destination","Protocol","Info","Risk"].map(h => <th key={h} style={s.th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {wireshark.packets.map((p, i) => (
                    <tr key={i}>
                      <td style={s.td}>{p.no}</td>
                      <td style={s.td}>{p.time}</td>
                      <td style={s.td}>{p.src}</td>
                      <td style={s.td}>{p.dst}</td>
                      <td style={s.td}>{p.protocol}</td>
                      <td style={s.td}>{p.info}</td>
                      <td style={s.td}><span style={s.badge(p.risk)}>{p.risk}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {metasploit && (
            <div style={{...s.card, marginBottom: 20}}>
              <div style={s.sectionTitle}>💀 Metasploit Attack Scenarios (Simulated)</div>
              <p style={{color: "#4a5568", fontSize: 12, marginBottom: 12}}>{metasploit.note}</p>
              {metasploit.scenarios.map((sc, i) => (
                <div key={i} style={{...s.recCard, borderLeft: `3px solid ${COLORS[sc.risk]}`}}>
                  <div style={{color: "#ff5252", fontFamily: "monospace", fontSize: 13}}>{sc.module}</div>
                  <div style={{color: "#a0b0cc", fontSize: 13, margin: "6px 0"}}>{sc.description}</div>
                  <div style={{color: "#6b7a99", fontSize: 12}}>Target: {sc.target}</div>
                  <div style={{color: "#00e676", fontSize: 12, marginTop: 4}}>Result: {sc.result}</div>
                  <span style={{...s.badge(sc.risk), marginTop: 6}}>{sc.risk}</span>
                </div>
              ))}
            </div>
          )}

          {burp && (
            <div style={s.card}>
              <div style={s.sectionTitle}>🕷️ Burp Suite / OWASP ZAP Findings (Simulated)</div>
              <p style={{color: "#4a5568", fontSize: 12, marginBottom: 12}}>{burp.note}</p>
              <table style={s.table}>
                <thead>
                  <tr>{["#","Type","Endpoint","Severity","Detail"].map(h => <th key={h} style={s.th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {burp.findings.map((f, i) => (
                    <tr key={i}>
                      <td style={s.td}>{f.id}</td>
                      <td style={s.td}>{f.type}</td>
                      <td style={{...s.td, fontFamily: "monospace", fontSize: 12}}>{f.endpoint}</td>
                      <td style={s.td}><span style={s.badge(f.severity)}>{f.severity}</span></td>
                      <td style={s.td}>{f.detail}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* RECOMMENDATIONS */}
      {tab === "Recommendations" && (
        <div>
          {recs.map((rec, i) => (
            <div key={i} style={{...s.recCard, borderLeft: `3px solid ${rec.priority === "Critical" ? "#ff1744" : rec.priority === "High" ? "#ff9100" : "#4f8ef7"}`}}>
              <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10}}>
                <div style={s.recTitle}>{rec.category}</div>
                <span style={s.badge(rec.priority === "Critical" ? "High" : rec.priority)}>{rec.priority}</span>
              </div>
              {rec.items.map((item, j) => (
                <div key={j} style={s.recItem}>• {item}</div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
