import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import CardInsert from "./pages/CardInsert";
import PinEntry from "./pages/PinEntry";
import ATMMenu from "./pages/ATMMenu";
import Withdraw from "./pages/Withdraw";
import MiniStatement from "./pages/MiniStatement";
import Dashboard from "./pages/Dashboard";
import Navbar from "./components/Navbar";

function PrivateRoute({ children }) {
  return localStorage.getItem("atm_token") ? children : <Navigate to="/" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/"           element={<CardInsert />} />
        <Route path="/pin"        element={<PinEntry />} />
        <Route path="/menu"       element={<PrivateRoute><ATMMenu /></PrivateRoute>} />
        <Route path="/withdraw"   element={<PrivateRoute><Withdraw /></PrivateRoute>} />
        <Route path="/statement"  element={<PrivateRoute><MiniStatement /></PrivateRoute>} />
        <Route path="/dashboard"  element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}
