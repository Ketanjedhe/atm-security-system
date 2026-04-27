import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

const s = {
  wrap: { display: "flex", justifyContent: "center", alignItems: "flex-start", minHeight: "80vh", paddingTop: 40 },
  box: { background: "#111827", border: "1px solid #1e2d4a", borderRadius: 16, padding: 32, width: 480 },
  title: { fontSize: 20, fontWeight: 700, color: "#4f8ef7", marginBottom: 20 },
  row: {
    display: "flex", justifyContent: "space-between", alignItems: "center",
    padding: "12px 0", borderBottom: "1px solid #1e2d4a"
  },
  type: { color: "#a0b0cc", fontSize: 13 },
  amount: { color: "#ff5252", fontWeight: 700, fontSize: 16 },
  date: { color: "#4a5568", fontSize: 12, marginTop: 2 },
  empty: { color: "#4a5568", textAlign: "center", padding: 32 },
  backBtn: { background: "#1a2540", color: "#a0b0cc", width: "100%", marginTop: 20 }
};

export default function MiniStatement() {
  const [txns, setTxns] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/transactions/mini-statement")
      .then(r => setTxns(r.data.transactions))
      .catch(() => navigate("/"))
      .finally(() => setLoading(false));
  }, [navigate]);

  return (
    <div style={s.wrap}>
      <div style={s.box}>
        <div style={s.title}>📋 Mini Statement (Last 5 Transactions)</div>
        {loading && <div style={s.empty}>Loading...</div>}
        {!loading && txns.length === 0 && <div style={s.empty}>No transactions found</div>}
        {txns.map((t, i) => (
          <div key={i} style={s.row}>
            <div>
              <div style={s.type}>{t.type}</div>
              <div style={s.date}>{new Date(t.timestamp).toLocaleString("en-IN")}</div>
            </div>
            <div>
              <div style={s.amount}>- ₹{t.amount?.toLocaleString("en-IN")}</div>
              <div style={{...s.date, textAlign: "right"}}>
                Bal: ₹{t.balance_after?.toLocaleString("en-IN")}
              </div>
            </div>
          </div>
        ))}
        <button style={s.backBtn} onClick={() => navigate("/menu")}>← Back to Menu</button>
      </div>
    </div>
  );
}
