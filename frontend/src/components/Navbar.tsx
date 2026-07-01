import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ChartIcon, SettingsIcon, PositionIcon, SignalIcon, TradeIcon, AdminIcon, LogoutIcon, MenuIcon, CloseIcon, BrainIcon, LightningIcon } from "./Icons";
import { useState } from "react";

export function AppNavbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navLinks = user ? [
    { label: "Dashboard", path: "/dashboard", icon: ChartIcon },
    { label: "Positions", path: "/positions", icon: PositionIcon },
    { label: "Signals", path: "/signals", icon: SignalIcon },
    { label: "Trades", path: "/trades", icon: TradeIcon },
    { label: "Strategies", path: "/strategy-performance", icon: BrainIcon },
    { label: "Backtest", path: "/backtesting", icon: LightningIcon },
    { label: "Plan", path: "/subscribe", icon: LightningIcon },
    { label: "Settings", path: "/settings", icon: SettingsIcon },
    ...(user?.is_admin ? [
      { label: "Users", path: "/admin", icon: AdminIcon },
      { label: "Analytics", path: "/admin/analytics", icon: ChartIcon },
    ] : []),
  ] : [];

  return (
    <nav className="glass-card-strong sticky top-0 z-50 border-b border-white/5">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-2.5 shrink-0 group">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-lg shadow-accent/20">
            <span className="text-white font-bold text-xs">N</span>
          </div>
          <span className="font-semibold text-sm tracking-wider hidden sm:block">
            <span className="neon-text-cyan">Nex</span><span className="neon-text-magenta">Trade</span>
          </span>
        </Link>

        <div className="hidden md:flex items-center gap-1">
          {navLinks.map((l) => (
            <button key={l.path} onClick={() => navigate(l.path)}
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-white hover:bg-white/5 px-3 py-1.5 rounded-md transition-all whitespace-nowrap"
            >
              <l.icon className="w-3.5 h-3.5" />
              {l.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="text-xs text-gray-600 hidden sm:block">{user.email}</span>
              <button onClick={logout} className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-negative px-3 py-2 rounded-md transition-colors">
                <LogoutIcon className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Logout</span>
              </button>
              <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden text-gray-500 p-2">
                {mobileOpen ? <CloseIcon /> : <MenuIcon />}
              </button>
            </>
          ) : (
            <div className="flex items-center gap-4">
              <a href="mailto:support@nextrade.ai" className="text-xs text-gray-500 hover:text-white transition-colors hidden sm:block">Support</a>
              <Link to="/login" className="text-xs text-gray-400 hover:text-white transition-colors">Sign In</Link>
              <Link to="/signup" className="text-xs bg-gradient-to-r from-accent to-accent-secondary hover:from-accent-dark hover:to-accent-secondary text-white px-4 py-1.5 rounded-md font-medium transition-all shadow-lg shadow-accent/20">
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>

      {mobileOpen && user && (
        <div className="md:hidden border-t border-white/5 bg-dark-900/95 backdrop-blur-xl">
          <div className="px-6 py-3 space-y-0.5">
            {navLinks.map((l) => (
              <button key={l.path} onClick={() => { navigate(l.path); setMobileOpen(false); }}
                className="flex items-center gap-3 w-full text-xs text-gray-400 hover:text-white hover:bg-white/5 px-3 py-2.5 rounded-md transition-all"
              >
                <l.icon className="w-4 h-4" />
                {l.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
}
