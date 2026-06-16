import { useState } from "react";
import { motion } from "framer-motion";
import { AppNavbar } from "../components/Navbar";
import { PageTransition } from "../components/PageTransition";
import { api } from "../api/client";

const PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "ADA/USDT", "DOGE/USDT", "XRP/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT"];
const STRATEGIES = ["rsi", "macd", "ema", "volume", "bollinger", "supertrend", "adx", "ichimoku"];

export default function Backtesting() {
  const [pair, setPair] = useState("BTC/USDT");
  const [strategy, setStrategy] = useState("rsi");
  const [days, setDays] = useState(30);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<{ status: string; message: string } | null>(null);

  const runBacktest = async () => {
    setRunning(true);
    setResult(null);
    try {
      const res = await api.runBacktest({ pair, strategy, days });
      setResult(res);
    } catch (e: any) {
      setResult({ status: "error", message: e.message || "Backtest failed" });
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-900 text-white">
      <AppNavbar />
      <PageTransition>
        <div className="max-w-3xl mx-auto px-6 py-16">
          <div className="mb-8">
            <h1 className="font-heading text-3xl md:text-4xl font-bold mb-2">Backtesting</h1>
            <p className="text-gray-400">Test strategies against historical data before going live</p>
          </div>

          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            className="bg-dark-800/40 border border-white/[0.06] rounded-2xl p-8"
          >
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div>
                <label className="block text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Trading Pair</label>
                <select value={pair} onChange={e => setPair(e.target.value)}
                  className="w-full bg-dark-900 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-accent/50 focus:outline-none"
                >
                  {PAIRS.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Strategy</label>
                <select value={strategy} onChange={e => setStrategy(e.target.value)}
                  className="w-full bg-dark-900 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-accent/50 focus:outline-none"
                >
                  {STRATEGIES.map(s => <option key={s} value={s}>{s.toUpperCase()}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2">Period (days)</label>
                <input type="number" value={days} onChange={e => setDays(Number(e.target.value))} min={7} max={365}
                  className="w-full bg-dark-900 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-accent/50 focus:outline-none"
                />
              </div>
            </div>

            <button onClick={runBacktest} disabled={running}
              className="w-full bg-accent hover:bg-accent-dark text-dark-900 font-bold py-3 rounded-xl transition-all shadow-lg shadow-accent/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {running ? "Running Backtest..." : "Run Backtest"}
            </button>

            {result && (
              <div className={`mt-6 p-4 rounded-xl text-sm ${
                result.status === "error"
                  ? "bg-red-500/10 border border-red-500/20 text-red-400"
                  : "bg-accent/10 border border-accent/20 text-accent"
              }`}>
                {result.message}
              </div>
            )}
          </motion.div>
        </div>
      </PageTransition>
    </div>
  );
}
