import { useState } from "react";
import { api } from "../api/client";

export default function ManualOverride() {
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [result, setResult] = useState<string | null>(null);

  const handleAction = async (action: string) => {
    try {
      const res = await api.override(action, symbol);
      setResult(res.success ? `${action} executed on ${symbol}` : "Failed");
    } catch (e) {
      setResult(`Error: ${e}`);
    }
  };

  return (
    <div>
      <h1>Manual Override</h1>
      <div style={{ marginBottom: "1rem" }}>
        <label>
          Symbol:{" "}
          <input
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            style={{ padding: "0.4rem", width: 200 }}
          />
        </label>
      </div>
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <button onClick={() => handleAction("buy")} style={btnStyle("green")}>
          BUY
        </button>
        <button onClick={() => handleAction("sell")} style={btnStyle("red")}>
          SELL
        </button>
        <button onClick={() => handleAction("close_all")} style={btnStyle("#dc3545")}>
          CLOSE ALL
        </button>
        <button onClick={() => handleAction("emergency_stop")} style={btnStyle("#333")}>
          EMERGENCY STOP
        </button>
      </div>
      {result && <p style={{ marginTop: "1rem" }}>{result}</p>}
    </div>
  );
}

function btnStyle(color: string): React.CSSProperties {
  return {
    padding: "0.6rem 1.5rem",
    background: color,
    color: "#fff",
    border: "none",
    borderRadius: 6,
    cursor: "pointer",
    fontWeight: 600,
  };
}
