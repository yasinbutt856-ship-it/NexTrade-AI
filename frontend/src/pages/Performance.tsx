import { useQuery } from "@tanstack/react-query";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../api/client";

export default function Performance() {
  const { data } = useQuery({ queryKey: ["performance"], queryFn: api.performance });

  return (
    <div>
      <h1>Performance</h1>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <div style={{ flex: 1, background: "#fff", padding: "1rem", borderRadius: 8 }}>
          <div style={{ fontSize: "0.8rem", color: "#888" }}>Total P&L</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700, color: (data?.total_pnl ?? 0) >= 0 ? "green" : "red" }}>
            ${(data?.total_pnl ?? 0).toFixed(2)}
          </div>
        </div>
        <div style={{ flex: 1, background: "#fff", padding: "1rem", borderRadius: 8 }}>
          <div style={{ fontSize: "0.8rem", color: "#888" }}>Win Rate</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{(data?.win_rate ?? 0).toFixed(1)}%</div>
        </div>
        <div style={{ flex: 1, background: "#fff", padding: "1rem", borderRadius: 8 }}>
          <div style={{ fontSize: "0.8rem", color: "#888" }}>Total Trades</div>
          <div style={{ fontSize: "1.5rem", fontWeight: 700 }}>{data?.total_trades ?? 0}</div>
        </div>
      </div>
      <div style={{ background: "#fff", padding: "1rem", borderRadius: 8 }}>
        <h2>Equity Curve</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data?.equity_curve}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#1a73e8" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
