import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Trades() {
  const { data: trades } = useQuery({ queryKey: ["trades"], queryFn: api.trades });

  return (
    <div>
      <h1>Trade History</h1>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", background: "#eee" }}>
            <th>Time</th>
            <th>Symbol</th>
            <th>Side</th>
            <th>Price</th>
            <th>Qty</th>
            <th>Total</th>
            <th>Fee</th>
          </tr>
        </thead>
        <tbody>
          {trades?.map((t, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #ddd" }}>
              <td>{new Date(t.timestamp).toLocaleString()}</td>
              <td>{t.symbol}</td>
              <td>{t.side.toUpperCase()}</td>
              <td>${t.price}</td>
              <td>{t.quantity}</td>
              <td>${t.total.toFixed(2)}</td>
              <td>${t.fee.toFixed(4)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
