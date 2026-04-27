import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

const s = {
  wrap: { display: "flex", justifyContent: "center", alignItems: "center", minHeight: "80vh" },
  box: {
    background: "#111827", border: "1px solid #1e2d4a", borderRadius: 16,
    padding: 40, width: 380, textAlign: "center"
  },
  icon: { fontSize: 64, marginBottom: 16 },
  title: { fontSize: 22, fontWeight: 700, color: "#4f8ef7", marginBottom: 8 },
  sub: { color: "#6b7a99", fontSize: 14, marginBottom: 24 },
  label: { display: "block", textAlign: "left", color: "#a0b0cc", fontSize: 13, marginBottom: 6 },
  btn: { background: "#4f8ef7", color: "#fff", width: "100%", marginTop: 16 },
  err: { color: "#ff5252", marginTop: 12, fontSize: 14 },
  hint: { color: "#4a5568", fontSize: 12, marginTop: 16 }
};

export default function CardInsert() {
  const [card, setCard] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (card.length !== 16 || !/^\d+$/.test(card)) {
      setError("Card number must be exactly 16 digits");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post("/auth/insert-card", { card_number: card });
      localStorage.setItem("atm_card", card);
      localStorage.setItem("atm_holder", res.data.card_holder);
      navigate("/pin");
    } catch (err) {
      setError(err.response?.data?.error || "Card not recognized");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={s.wrap}>
      <div style={s.box}>
        <div style={s.icon}>💳</div>
        <div style={s.title}>Insert Your Card</div>
        <div style={s.sub}>Enter your 16-digit card number to begin</div>
        <form onSubmit={handleSubmit}>
          <label style={s.label}>Card Number</label>
          <input
            type="text"
            maxLength={16}
            placeholder="1234 5678 9012 3456"
            value={card}
            onChange={(e) => setCard(e.target.value.replace(/\D/g, ""))}
            aria-label="Card number"
          />
          {error && <div style={s.err}>{error}</div>}
          <button type="submit" style={s.btn} disabled={loading}>
            {loading ? "Verifying..." : "Insert Card →"}
          </button>
        </form>
        <div style={s.hint}>
          Test card: 4111111111111111
        </div>
      </div>
    </div>
  );
}
