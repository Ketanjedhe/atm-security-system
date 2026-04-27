import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

const s = {
  wrap: { display: "flex", justifyContent: "center", alignItems: "center", minHeight: "80vh" },
  box: {
    background: "#111827", border: "1px solid #1e2d4a", borderRadius: 16,
    padding: 40, width: 380, textAlign: "center"
  },
  icon: { fontSize: 56, marginBottom: 12 },
  title: { fontSize: 22, fontWeight: 700, color: "#4f8ef7", marginBottom: 6 },
  sub: { color: "#6b7a99", fontSize: 14, marginBottom: 24 },
  label: { display: "block", textAlign: "left", color: "#a0b0cc", fontSize: 13, marginBottom: 6 },
  pinRow: { display: "flex", gap: 10, justifyContent: "center", marginBottom: 20 },
  pinDot: (filled) => ({
    width: 18, height: 18, borderRadius: "50%",
    background: filled ? "#4f8ef7" : "#1e2d4a",
    border: "2px solid #4f8ef7", transition: "background 0.2s"
  }),
  numpad: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 16 },
  numBtn: {
    background: "#1a2540", color: "#e0e6f0", fontSize: 20, fontWeight: 700,
    padding: "14px 0", borderRadius: 8, border: "1px solid #2a3a5c"
  },
  clearBtn: { background: "#ff5252", color: "#fff", width: "100%", marginBottom: 8 },
  submitBtn: { background: "#4f8ef7", color: "#fff", width: "100%" },
  err: { color: "#ff5252", marginTop: 12, fontSize: 14 },
  holder: { color: "#4f8ef7", fontWeight: 600, marginBottom: 16 }
};

export default function PinEntry() {
  const [pin, setPin] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const card = localStorage.getItem("atm_card");
  const holder = localStorage.getItem("atm_holder");

  const pressKey = (k) => { if (pin.length < 4) setPin(p => p + k); };
  const clearPin = () => setPin("");

  const handleSubmit = async () => {
    if (pin.length !== 4) { setError("PIN must be 4 digits"); return; }
    setError(""); setLoading(true);
    try {
      const res = await api.post("/auth/verify-pin", { card_number: card, pin });
      localStorage.setItem("atm_token", res.data.token);
      localStorage.setItem("atm_user_id", res.data.user_id);
      localStorage.setItem("atm_balance", res.data.balance);
      navigate("/menu");
    } catch (err) {
      setError(err.response?.data?.error || "Authentication failed");
      setPin("");
    } finally {
      setLoading(false);
    }
  };

  const keys = ["1","2","3","4","5","6","7","8","9","","0","⌫"];

  return (
    <div style={s.wrap}>
      <div style={s.box}>
        <div style={s.icon}>🔐</div>
        <div style={s.title}>Enter PIN</div>
        {holder && <div style={s.holder}>Welcome, {holder}</div>}
        <div style={s.sub}>Enter your 4-digit PIN</div>

        <div style={s.pinRow}>
          {[0,1,2,3].map(i => <div key={i} style={s.pinDot(i < pin.length)} />)}
        </div>

        <div style={s.numpad}>
          {keys.map((k, i) => (
            <button
              key={i}
              style={s.numBtn}
              onClick={() => k === "⌫" ? setPin(p => p.slice(0,-1)) : k ? pressKey(k) : null}
              disabled={!k}
              aria-label={k || "empty"}
            >{k}</button>
          ))}
        </div>

        {error && <div style={s.err}>{error}</div>}
        <button style={s.clearBtn} onClick={clearPin}>Clear</button>
        <button style={s.submitBtn} onClick={handleSubmit} disabled={loading || pin.length !== 4}>
          {loading ? "Verifying..." : "Confirm PIN"}
        </button>
      </div>
    </div>
  );
}
