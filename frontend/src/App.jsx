import { useEffect, useState } from "react";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area } from "recharts";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [tab, setTab] = useState("dashboard");
  const [items, setItems] = useState([]);
  const [item, setItem] = useState("Tomatoes");
  const [days, setDays] = useState(7);
  const [data, setData] = useState(null);
  const [admin, setAdmin] = useState(false);
  const [login, setLogin] = useState({ u: "", p: "" });

  useEffect(() => {
    axios.get(`${API}/items`).then(r => {
      setItems(r.data.items);
      if (r.data.items.length) setItem(r.data.items[0]);
    }).catch(() => setItems(["Tomatoes", "Sukuma Wiki", "Onions", "Maize", "Potatoes", "Cabbage"]));
  }, []);

  useEffect(() => {
    if (tab !== "dashboard") return;
    Promise.all([
      axios.get(`${API}/prices`, { params: { item, limit: 60 } }),
      axios.get(`${API}/predict`, { params: { item, days } })
    ]).then(([h, p]) => setData({ h: h.data, p: p.data })).catch(() => setData(null));
  }, [item, days, tab]);

  const chart = data ? [
    ...data.h.history.map(x => ({ date: x.date.slice(5), past: x.price })),
    ...data.p.forecast.map((x, i) => ({ date: x.date.slice(5), pred: x.predicted, lo: x.lower, hi: x.upper }))
  ] : [];

  const exportCSV = () => {
    if (!data) return;
    const rows = ["date,predicted,lower,upper", ...data.p.forecast.map(r => `${r.date},${r.predicted},${r.lower},${r.upper}`)];
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([rows.join("\n")], { type: "text/csv" }));
    a.download = `${item}_${days}day_forecast.csv`; a.click();
  };

  const upload = async (e) => {
    const f = e.target.files[0]; if (!f) return;
    const fd = new FormData(); fd.append("file", f);
    await axios.post(`${API}/upload`, fd);
    alert("Uploaded + retrained. Refresh dashboard.");
  };

  return (
    <div style={{ fontFamily: "Arial", maxWidth: 1000, margin: "0 auto", padding: 20 }}>
      <h1>AI Food Price Forecasting - Kenya</h1>
      <p>Historical + AI predicted prices for Wakulima market. Simulated near-real-time demo.</p>
      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        {["dashboard", "predictions", "admin", "login"].map(t => (
          <button key={t} onClick={() => setTab(t)} style={{ padding: "8px 16px", background: tab === t ? "#16a34a" : "#eee", color: tab === t ? "#fff" : "#000", border: 0, borderRadius: 6 }}>{t}</button>
        ))}
      </div>

      {tab === "dashboard" && (
        <div>
          <div style={{ display: "flex", gap: 10, marginBottom: 15 }}>
            <select value={item} onChange={e => setItem(e.target.value)}>{items.map(i => <option key={i}>{i}</option>)}</select>
            <select value={days} onChange={e => setDays(Number(e.target.value))}><option value={7}>Next 7 days</option><option value={14}>Next 14 days</option><option value={30}>Next 30 days</option></select>
            <button onClick={exportCSV}>Export CSV</button>
          </div>
          {data ? <>
            <div style={{ background: "#f0fdf4", padding: 12, borderRadius: 8, marginBottom: 12 }}>
              <b>Current: {data.h.current} KES</b> | Trend: <b>{data.p.trend}</b><br />{data.p.recommendation}
            </div>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={chart}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis /><Tooltip /><Legend />
                <Line type="monotone" dataKey="past" stroke="#8884d8" name="Past" dot={false} />
                <Line type="monotone" dataKey="pred" stroke="#16a34a" name="Predicted" strokeWidth={2} />
                <Line type="monotone" dataKey="lo" stroke="#ccc" name="Lower" dot={false} />
                <Line type="monotone" dataKey="hi" stroke="#ccc" name="Upper" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </> : <p>Start backend: backend\venv312\Scripts\python -m uvicorn backend.main:app --port 8000</p>}
        </div>
      )}

      {tab === "predictions" && <div><h3>Predictions</h3><p>Select item + days on Dashboard. Forecast shows predicted price + confidence range + best-time-to-buy.</p></div>}

      {tab === "admin" && (
        <div>{admin ? <><h3>Admin Upload</h3><p>CSV columns: date,item,market,price_kes,unit</p><input type="file" accept=".csv" onChange={upload} /></> : <p>Login first on Login tab (admin/admin).</p>}</div>
      )}

      {tab === "login" && (
        <div>
          <h3>Admin Login</h3>
          <input placeholder="user" value={login.u} onChange={e => setLogin({ ...login, u: e.target.value })} />{" "}
          <input placeholder="pass" type="password" value={login.p} onChange={e => setLogin({ ...login, p: e.target.value })} />{" "}
          <button onClick={() => { if (login.u === "admin" && login.p === "admin") { setAdmin(true); alert("Logged in - now go to Admin tab"); } else { alert("Use admin/admin for MVP"); } }}>Login</button>
        </div>
      )}
    </div>
  );
}
