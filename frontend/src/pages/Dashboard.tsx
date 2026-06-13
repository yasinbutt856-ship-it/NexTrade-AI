import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export default function Dashboard() {
  const { data: status } = useQuery({ queryKey: ["status"], queryFn: api.status });
  const { data: positions } = useQuery({ queryKey: ["positions"], queryFn: api.positions });
  const { data: signals } = useQuery({ queryKey: ["signals"], queryFn: api.signals });

  const totalPnl = positions?.reduce((s, p) => s + p.unrealized_pnl + p.realized_pnl, 0) ?? 0;

  return (
    <div>
      <h1>Dashboard</h1>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <Card label="Mode" value={status?.mode ?? "—"} />
        <Card label="P&L" value={`$${totalPnl.toFixed(2)}`} color={totalPnl >= 0 ? "green" : "red"} />
        <Card label="Open Positions" value={positions?.length ?? 0} />
        <Card label="Analyst" value={status?.analyst_alive ? "🟢 Alive" : "🔴 Dead"} />
        <Card label="Trader" value={status?.trader_alive ? "🟢 Alive" : "🔴 Dead"} />
      </div>
      <section>
        <h2>Latest Signals</h2>
        <pre>{JSON.stringify(signals?.slice(0, 5), null, 2)}</pre>
      </section>
    </div>
  );
}

function Card({ label, value, color }: { label: string; value: string | number; color?: string }) {
  return (
    <div
      style={{
        flex: 1,
        background: "#fff",
        padding: "1rem",
        borderRadius: 8,
        boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
      }}
    >
      <div style={{ fontSize: "0.8rem", color: "#888" }}>{label}</div>
      <div style={{ fontSize: "1.5rem", fontWeight: 700, color }}>{value}</div>
    </div>
  );
}
