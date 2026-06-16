import { motion } from "framer-motion";
import { AppNavbar } from "../components/Navbar";
import { PageTransition } from "../components/PageTransition";
import { ShieldIcon, KeyIcon, EyeIcon, FlaskIcon, ClockIcon, BotIcon } from "../components/Icons";

const sections = [
  { Icon: ShieldIcon, title: "AES-256 Encryption at Rest", desc: "All MEXC API keys are encrypted using Fernet (AES-256) before storage. The encryption key is never logged or exposed. Even if the database is compromised, your keys remain protected." },
  { Icon: KeyIcon, title: "Zero-Knowledge Architecture", desc: "We never custody your funds. You connect restricted MEXC API keys that can trade but cannot withdraw. Your funds stay on the exchange at all times." },
  { Icon: EyeIcon, title: "Full Transparency", desc: "Every trade, signal, and position is visible in real-time on your dashboard. No black boxes, no hidden logic. What you see is what the bot executes." },
  { Icon: FlaskIcon, title: "Paper Trading Sandbox", desc: "Test every strategy risk-free with paper trading mode. The bot simulates fills with realistic slippage and spread calculations before you risk real capital." },
  { Icon: ClockIcon, title: "Real-Time Monitoring", desc: "Analyst and trader heartbeats are monitored via Redis every 15 seconds. If either service goes offline, alerts fire instantly." },
  { Icon: ShieldIcon, title: "Risk Safeguards", desc: "Circuit breaker stops all trading at 10% drawdown. Daily loss limits, trailing stop-loss, and cooldown periods prevent cascade failures." },
  { Icon: BotIcon, title: "Multi-Tenant Isolation", desc: "Each user operates in an isolated session. Your MEXC keys, positions, and settings are never accessible to other users." },
  { Icon: KeyIcon, title: "JWT Authentication", desc: "All API requests require HS256 JWT tokens with 24-hour expiry. Tokens are signed server-side with a secret never exposed to the client." },
];

export default function Security() {
  return (
    <div className="min-h-screen bg-dark-900 text-white">
      <AppNavbar />
      <PageTransition>
        <div className="max-w-4xl mx-auto px-6 py-16">
          <div className="text-center mb-16">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent/20 to-blue-accent/20 flex items-center justify-center mx-auto mb-6">
              <ShieldIcon className="w-8 h-8 text-accent" />
            </div>
            <h1 className="font-heading text-4xl md:text-5xl font-bold mb-4">Security & Trust</h1>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg leading-relaxed">
              We built NexTrade AI with security as the foundation, not an afterthought. Your API keys, funds, and data are protected at every layer.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-5 mb-12">
            {sections.map((s, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.05 }}
                className="bg-dark-800/40 border border-white/[0.06] rounded-2xl p-6 hover:border-accent/20 transition-all"
              >
                <div className="w-10 h-10 mb-4 rounded-xl bg-accent/10 flex items-center justify-center">
                  <s.Icon className="w-5 h-5 text-accent" />
                </div>
                <h3 className="font-heading font-bold text-sm mb-2">{s.title}</h3>
                <p className="text-gray-400 text-xs leading-relaxed">{s.desc}</p>
              </motion.div>
            ))}
          </div>

          <div className="bg-dark-800/40 border border-white/[0.06] rounded-2xl p-8 text-center">
            <h2 className="font-heading text-2xl font-bold mb-4">Questions about security?</h2>
            <p className="text-gray-400 text-sm mb-4">Contact us at <a href="mailto:support@nextrade.ai" className="text-accent hover:underline">support@nextrade.ai</a></p>
            <p className="text-gray-500 text-xs">NexTrade AI Ltd. · Larnaca, Cyprus</p>
          </div>
        </div>
      </PageTransition>
    </div>
  );
}
