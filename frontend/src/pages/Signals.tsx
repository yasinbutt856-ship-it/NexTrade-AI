import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Signals() {
  const { data: signals } = useQuery({ queryKey: ["signals"], queryFn: api.signals });

  return (
    <div>
      <h1>Signals</h1>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", background: "#eee" }}>
            <th>Time</th>
            <th>Symbol</th>
            <th>Action</th>
            <th>Confidence</th>
            <th>Price</th>
            <th>Strategies</th>
          </tr>
        </thead>
        <tbody>
          {signals?.map((s, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #ddd" }}>
              <td>{new Date(s.timestamp).toLocaleString()}</td>
              <td>{s.symbol}</td>
              <td>{s.action.toUpperCase()}</td>
              <td>{(s.confidence * 100).toFixed(0)}%</td>
              <td>${s.price}</td>
              <td>{s.strategy_results.map((r) => r.strategy_name).join(", ")}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
