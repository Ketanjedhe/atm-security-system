import React from "react";
import { Link, useNavigate } from "react-router-dom";

const styles = {
  nav: {
    background: "#0d1526",
    borderBottom: "1px solid #1e2d4a",
    padding: "12px 32px",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between"
  },
  brand: { color: "#4f8ef7", fontWeight: 700, fontSize: 18, textDecoration: "none" },
  links: { display: "flex", gap: 20 },
  link: { color: "#a0b0cc", textDecoration: "none", fontSize: 14 },
  btn: { background: "#ff1744", color: "#fff", padding: "6px 14px", fontSize: 13 }
};

export default function Navbar() {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem("atm_token");

  const logout = () => {
    localStorage.clear();
    navigate("/");
  };

  return (
    <nav style={styles.nav}>
      <Link to="/" style={styles.brand}>🏧 ATM Security System</Link>
      <div style={styles.links}>
        <Link to="/" style={styles.link}>ATM</Link>
        <Link to="/dashboard" style={styles.link}>Security Dashboard</Link>
        {isLoggedIn && (
          <button style={styles.btn} onClick={logout}>Logout</button>
        )}
      </div>
    </nav>
  );
}
