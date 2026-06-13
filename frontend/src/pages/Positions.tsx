import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Positions() {
  const { data: positions } = useQuery({ queryKey: ["positions"], queryFn: api.positions });

  return (
    <div>
      <h1>Positions</h1>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", background: "#eee" }}>
            <th>Symbol</th>
            <th>Side</th>
            <th>Entry</th>
            <th>Current</th>
            <th>Qty</th>
            <th>Unrealized P&L</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {positions?.map((p) => (
            <tr key={p.id} style={{ borderBottom: "1px solid #ddd" }}>
              <td>{p.symbol}</td>
              <td>{p.side.toUpperCase()}</td>
              <td>${p.entry_price}</td>
              <td>${p.current_price}</td>
              <td>{p.quantity}</td>
              <td style={{ color: p.unrealized_pnl >= 0 ? "green" : "red" }}>
                ${p.unrealized_pnl.toFixed(2)}
              </td>
              <td>{p.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
