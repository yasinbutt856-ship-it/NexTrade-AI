import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { AppNavbar } from "../components/Navbar";
import { PageTransition } from "../components/PageTransition";
import { api } from "../api/client";
import { Badge } from "../components/ui/Badge";
import { useToast } from "../context/ToastContext";

export default function StrategyPerformance() {
  const { addToast } = useToast();
  const [data, setData] = useState<Record<string, { signals: number; wins: number; losses: number; total_pnl: number; win_rate: number; avg_confidence: number }> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.strategyPerformance().then(setData).catch(() => { addToast("Failed to load strategy data", "error"); }).finally(() => setLoading(false));
  }, []);

  const entries = data ? Object.entries(data).sort((a, b) => b[1].total_pnl - a[1].total_pnl) : [];

  return (
    <div className="min-h-screen bg-dark-900 text-white">
      <AppNavbar />
      <PageTransition>
        <div className="max-w-5xl mx-auto px-6 py-16">
          <div className="mb-8">
            <h1 className="font-heading text-3xl md:text-4xl font-bold mb-2">Strategy Performance</h1>
            <p className="text-gray-400">Win rate, P&L, and signal count per strategy</p>
          </div>

          {loading ? (
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-20 bg-dark-800/40 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : entries.length === 0 ? (
            <div className="text-center py-20 text-gray-500">
              <p>No strategy data yet. Signals need to be generated first.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {entries.map(([name, stats], i) => (
                <motion.div key={name} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                  className="bg-dark-800/40 border border-white/[0.06] rounded-xl p-5 hover:border-accent/20 transition-all"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-heading font-bold capitalize">{name}</h3>
                    <Badge variant={stats.win_rate >= 50 ? "success" : "error"}>{(stats.win_rate + "% win rate")}</Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-gray-500 text-xs">Signals</div>
                      <div className="font-semibold">{stats.signals}</div>
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs">Wins / Losses</div>
                      <div className="font-semibold">{stats.wins} / {stats.losses}</div>
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs">Total P&L</div>
                      <div className={`font-semibold ${stats.total_pnl >= 0 ? "text-green-400" : "text-red-400"}`}>
                        ${stats.total_pnl.toFixed(2)}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs">Avg Confidence</div>
                      <div className="font-semibold">{stats.avg_confidence}%</div>
                    </div>
                  </div>
                  <div className="mt-3 h-1.5 bg-dark-900 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-green-500 to-accent rounded-full" style={{ width: `${stats.win_rate}%` }} />
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </PageTransition>
    </div>
  );
}
