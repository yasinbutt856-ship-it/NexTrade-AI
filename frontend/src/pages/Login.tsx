import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { motion } from "framer-motion";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center px-6">
      <div className="fixed top-1/3 -left-32 w-96 h-96 bg-accent/8 rounded-full blur-[128px] pointer-events-none" />
      <div className="fixed bottom-1/3 -right-32 w-96 h-96 bg-accent-secondary/8 rounded-full blur-[128px] pointer-events-none" />
      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent to-accent-secondary flex items-center justify-center shadow-lg shadow-accent/20">
              <span className="text-white font-bold text-sm">N</span>
            </div>
            <span className="font-bold text-lg tracking-wider"><span className="neon-text-cyan">Nex</span><span className="neon-text-magenta">Trade</span></span>
          </Link>
          <h1 className="text-2xl font-bold">Welcome Back</h1>
          <p className="text-gray-400 text-sm mt-1">Sign in to your trading dashboard</p>
        </div>

        <motion.form initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} onSubmit={handleSubmit} className="glass-card rounded-2xl p-8 space-y-5">
          {error && (
            <div className="bg-negative/15 border border-negative/20 text-negative text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1.5">Email</label>
            <input
              type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-dark-800 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-all"
              placeholder="you@example.com" required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1.5">Password</label>
            <input
              type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-dark-800 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20 transition-all"
              placeholder="••••••••" required
            />
            <div className="flex justify-end mt-1.5">
              <Link to="/forgot-password" className="text-xs text-gray-500 hover:text-accent transition-colors">Forgot password?</Link>
            </div>
          </div>

          <button
            type="submit" disabled={loading}
            className="w-full bg-gradient-to-r from-accent to-accent-secondary hover:from-accent-dark hover:to-accent-secondary text-white font-bold py-3 rounded-xl transition-all disabled:opacity-50 shadow-lg shadow-accent/20"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>

          <p className="text-center text-sm text-gray-500">
            Don't have an account?{" "}
            <Link to="/signup" className="text-accent hover:underline">Sign up</Link>
          </p>
        </motion.form>
      </div>
    </div>
  );
}
