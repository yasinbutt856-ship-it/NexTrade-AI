import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";

const navItems = [
  { to: "/", label: "Dashboard", icon: "📊" },
  { to: "/positions", label: "Positions", icon: "💼" },
  { to: "/signals", label: "Signals", icon: "📡" },
  { to: "/trades", label: "Trades", icon: "📋" },
  { to: "/performance", label: "Performance", icon: "📈" },
  { to: "/settings", label: "Settings", icon: "⚙️" },
  { to: "/override", label: "Manual Override", icon: "🛑" },
];

export function Layout({ children }: { children: ReactNode }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <nav
        style={{
          width: 220,
          background: "#1a1a2e",
          color: "#eee",
          padding: "1rem",
        }}
      >
        <h2 style={{ fontSize: "1rem", marginBottom: "1.5rem" }}>MEXC Bot</h2>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              display: "block",
              padding: "0.5rem 0.75rem",
              marginBottom: "0.25rem",
              borderRadius: 6,
              textDecoration: "none",
              color: isActive ? "#fff" : "#aaa",
              background: isActive ? "#16213e" : "transparent",
            })}
          >
            {item.icon} {item.label}
          </NavLink>
        ))}
      </nav>
      <main style={{ flex: 1, padding: "1.5rem", background: "#f5f5f5" }}>
        {children}
      </main>
    </div>
  );
}
