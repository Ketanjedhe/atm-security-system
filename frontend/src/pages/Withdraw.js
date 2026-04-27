import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

const QUICK_AMOUNTS = [500, 1000, 2000, 5000, 10000, 20000];

const s = {
  wrap: { display: "flex", justifyContent: "center", alignItems: "center", minHeight: "80vh" },
  box: {
    background: "#111827", border: "1px solid #1e2d4a", borderRadius: 16,
    padding: 40, width: 420
  },
  title: { fontSize: 22, fontWeight: 700, color: "#4f8ef7", marginBottom: 20, textAlign: "center" },
  label: { color: "#a0b0cc", fontSize: 13, marginBottom: 6, display: "block" },
  quickGrid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, margin: "16px 0" },
  quickBtn: (sel) => ({
    background: sel ? "#4f8ef7" : "#1a2540",
    color: sel ? "#fff" : "#a0b0cc",
    border: `1px solid ${sel ? "#4f8ef7" : "#2a3a5c"}`,
    padding: "12px 0", borderRadius: 8, fontSize: 14, fontWeight: 600
  }),
  submitBtn: { background: "#4f8ef7", color: "#fff", width: "100%", marginTop: 16 },
  backBtn: { background: "#1a2540", color: "#a0b0cc", width: "100%", marginTop: 8 },
  err: { color: "#ff5252", marginTop: 10, fontSize: 14 },
  success: {
    background: "#0a2a1a", border: "1px solid #00c853", borderRadius: 10,
    padding: 24, textAlign: "center", marginTop: 16
  },
  successIcon: { fontSize: 48, marginBottom: 8 },
  successTitle: { color: "#00e676", fontSize: 20, fontWeight: 700 },
  successSub: { color: "#a0b0cc", fontSize: 14, marginTop: 6 }
};

export default function Withdraw() {
  const [amount, setAmount] = useState("");
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const navigate = useNavigate();

  const selectQuick = (val) => { setSelected(val); setAmount(String(val)); setError(""); };

  const handleWithdraw = async () => {
    const amt = parseInt(amount);
    if (!amt || amt <= 0) { setError("Enter a valid amount"); return; }
    setError(""); setLoading(true);
    try {
      const res = await api.post("/transactions/withdraw", { amount: amt });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || "Transaction failed");
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div style={s.wrap}>
        <div style={s.box}>
          <div style={s.success}>
            <div style={s.successIcon}>✅</div>
            <div style={s.successTitle}>{result.message}</div>
            <div style={s.successSub}>Remaining balance: ₹{result.balance_after?.toLocaleString("en-IN")}</div>
            <div style={{...s.successSub, marginTop: 4, fontSize: 12}}>
              Please collect your cash
            </div>
          </div>
          <button style={s.submitBtn} onClick={() => navigate("/menu")}>Back to Menu</button>
        </div>
      </div>
    );
  }

  return (
    <div style={s.wrap}>
      <div style={s.box}>
        <div style={s.title}>💵 Cash Withdrawal</div>
        <label style={s.label}>Quick Select Amount</label>
        <div style={s.quickGrid}>
          {QUICK_AMOUNTS.map(a => (
            <button key={a} style={s.quickBtn(selected === a)} onClick={() => selectQuick(a)}>
              ₹{a.toLocaleString("en-IN")}
            </button>
          ))}
        </div>
        <label style={s.label}>Or Enter Custom Amount (multiples of ₹100)</label>
        <input
          type="number"
          placeholder="e.g. 1500"
          value={amount}
          onChange={(e) => { setAmount(e.target.value); setSelected(null); }}
          aria-label="Withdrawal amount"
        />
        {error && <div style={s.err}>{error}</div>}
        <button style={s.submitBtn} onClick={handleWithdraw} disabled={loading || !amount}>
          {loading ? "Processing..." : "Withdraw"}
        </button>
        <button style={s.backBtn} onClick={() => navigate("/menu")}>← Back</button>
      </div>
    </div>
  );
}
