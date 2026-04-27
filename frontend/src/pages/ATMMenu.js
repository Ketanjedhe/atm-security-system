import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

const s = {
  wrap: { display: "flex", justifyContent: "center", alignItems: "center", minHeight: "80vh" },
  box: {
    background: "#111827", border: "1px solid #1e2d4a", borderRadius: 16,
    padding: 40, width: 420, textAlign: "center"
  },
  title: { fontSize: 22, fontWeight: 700, color: "#4f8ef7", marginBottom: 6 },
  balance: { fontSize: 32, fontWeight: 800, color: "#00e676", margin: "16px 0" },
  label: { color: "#6b7a99", fontSize: 13 },
  grid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginTop: 24 },
  menuBtn: (color) => ({
    background: color, color: "#fff", padding: "18px 0",
    borderRadius: 10, fontSize: 15, fontWeight: 600
  }),
  time: { color: "#4a5568", fontSize: 12, marginTop: 20 }
};

export default function ATMMenu() {
  const [balance, setBalance] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/transactions/balance")
      .then(r => setBalance(r.data.balance))
      .catch(() => navigate("/"));
  }, [navigate]);

  const logout = async () => {
    await api.post("/auth/logout").catch(() => {});
    localStorage.clear();
    navigate("/");
  };

  return (
    <div style={s.wrap}>
      <div style={s.box}>
        <div style={s.title}>🏧 ATM Services</div>
        <div style={s.label}>Available Balance</div>
        <div style={s.balance}>
          {balance !== null ? `₹${balance.toLocaleString("en-IN")}` : "Loading..."}
        </div>

        <div style={s.grid}>
          <button style={s.menuBtn("#4f8ef7")} onClick={() => navigate("/withdraw")}>
            💵 Withdraw Cash
          </button>
          <button style={s.menuBtn("#7c3aed")} onClick={() => navigate("/statement")}>
            📋 Mini Statement
          </button>
          <button style={s.menuBtn("#059669")} onClick={() => navigate("/dashboard")}>
            🛡️ Security Audit
          </button>
          <button style={s.menuBtn("#dc2626")} onClick={logout}>
            🚪 Exit / Logout
          </button>
        </div>
        <div style={s.time}>Session active · {new Date().toLocaleTimeString()}</div>
      </div>
    </div>
  );
}
