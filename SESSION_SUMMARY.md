# Project Summary

## Goal
Fully autonomous two-bot trading system (Market Analyst + Trader Bot) for MEXC spot & futures sold as SaaS subscription (3 tiers), multi-tenant accounts, encrypted API keys, JWT auth, crypto wallet (EVM + Solana), dark Tailwind v4 React frontend.

## Stack
- **Backend**: Python 3.12, FastAPI, ccxt, yfinance/CoinGecko, Redis pub/sub, Pydantic v2, structlog, PostgreSQL (Railway) / SQLite (dev)
- **Frontend**: React 19, Vite 8, Tailwind v4, Recharts, ethers, @solana/web3.js
- **Infra**: Railway (backend + bots + DB + Redis), Netlify (frontend), GitHub

## Done (Expanded)
- **Analyst/Trader DEAD fixed**: `lpush` for signals, 15s heartbeat caches, status endpoint reads `settings.yaml` mode correctly
- **JWT auth**: bcrypt hash/verify, JWT create/decode (HS256, 24h), register/login/me with Bearer middleware
- **Admin seed**: `abeermeer7979@gmail.com` / `Abeer@123` (enterprise, is_admin) on startup
- **MEXC key mgmt**: Fernet AES-256 encrypt/decrypt via `shared/encryption.py`, PUT/GET endpoints
- **User settings API**: paper/live, spot/futures, max_position, bot start/stop via Redis pub/sub `bot:control`
- **Admin user list**: GET /api/user/admin/users — all users with plan/mode/bot_active/MEXC status
- **Full frontend**: 22 pages — Landing, Login, Signup, VerifyEmail, ForgotPassword, ResetPassword, Dashboard, Settings, Admin, AdminAnalytics, Positions, Signals, Trades, StrategyPerformance, Backtesting, Status, Docs, Terms, Privacy, Whitepaper, About, Changelog, Security — all dark themed with code splitting
- **Multi-tenant trader**: per-user UserSession with PaperEngine/RiskManager/PositionTracker/MEXCClient, signal execution per user_id
- **Wallet (EVM + Solana)**: SIWE nonce, eth_account recover, nacl verify; endpoints + WalletContext + WalletConnect (MetaMask + Phantom)
- **Plan enforcement**: `shared/plan_limits.py` — tier limits + usage caps + trial enforcement
- **18 revenue-ready features**: strategy perf, portfolio, CSV export, backtesting UI, custom pairs, notification prefs, user API keys, admin analytics, trial status, usage tracking, GDPR export/delete
- **Platform depth**: code splitting (336KB max), dark/light mode, toast notifications, loading skeletons, error boundaries, sortable tables, WebSocket real-time
- **7 trust pages**: Terms, Privacy, Whitepaper, Security, Changelog, About, Status — plus company footer, support email, SLA commitment
- **64 backend tests passing**, frontend test setup (vitest + testing-library)
- **README**: fully updated with all 50+ API endpoints, full project structure, all features

## Completed This Session (18-Item Overhaul)

### 🔴 Critical
1. **MEXC API key validation** — Implemented `validate_credentials()` in `MEXCClient` that calls `fetch_balance()` on spot + futures. `PUT /api/user/mexc-keys` now validates before saving (rejects fake keys with 400). `POST /api/user/bot` blocks live start if unverified. `UserSession.__init__` calls `validate_exchange()` on session creation. Frontend shows "Verifying with MEXC..." → ✅ status badges per spot/futures. (7 files changed)

### 🟡 Blocked (skipped)
2. Custom domain — no domain purchased yet
3. Stripe/PayPal — no Stripe account yet
14. Subscription management UI — depends on Stripe

### 🟠 Implemented
4. **Usage-based enforcement** — Added `max_api_calls_per_day`, `max_bot_hours_per_month`, `max_trade_volume_per_month` to `PLAN_LIMITS` per tier. Added `enforce_usage_limit()` and `get_usage_limits()` functions.
5. **CI/CD pipeline** — Created `.github/workflows/test.yml` (backend tests + frontend build on push/PR) and `.github/workflows/deploy.yml` (auto-deploy frontend to Netlify from GitHub Actions).
6. **Frontend tests** — Installed vitest + @testing-library/react + jsdom. Created `__tests__/setup.ts` and `App.test.tsx` basic smoke test. Added `test` script to package.json. Vite config now uses `vitest/config`.
7. **Plan enforcement in trader** — Added `plan` field to `UserSession`, imports plan limits from `plan_limits.py`. `_execute_for_user` now checks `spot_only` and `max_pairs` before trading. RiskManager draws `max_position_size_usdt` from user's plan.
8. **Email templates** — Created `trader/templates/` with 4 branded HTML templates (dark theme): `verify_email.html`, `reset_password.html`, `welcome.html`, `trade_notification.html`. Updated `Notifier.send_custom_email()` to support multi-part (plain + HTML). Auth router now sends HTML verification, reset, and welcome emails.
9. **netlify.toml** — Created `frontend/netlify.toml` with build command, publish directory, and SPA redirect rules (replaces `public/_redirects`).
10. **Onboarding email** — Registration now sends branded "Welcome to NexTrade AI - Getting Started" email with setup steps (get MEXC keys → connect in Settings → start paper trading).
11. **Status page** — Created `/status` page at `frontend/src/pages/Status.tsx` with live service checks (health endpoint, analyst/trader alive), uptime display, latency per service, SLA commitment table (Basic/Pro/Enterprise). Added to App.tsx routes and footer links.
12. **Error handling** — Fixed silent `catch(() => {})` in StrategyPerformance and AdminAnalytics pages — now shows error toasts via `useToast()`.

### 🔵 Still Pending
6/13. **Backtesting engine** — endpoint is still a placeholder (`{"status": "queued"}`), no real historical data fetch or strategy execution
12. **Multi-exchange (Binance + Bybit)** — exchange clients not yet created
15. **Docker Desktop** — not running locally, can't test containers
16. **Mobile polish** — basic responsive patterns exist, need full audit
17. **Multi-exchange** — Binance + Bybit requested

## Remaining
1. Real backtesting engine (fetch historical data + run strategies)
2. Binance + Bybit exchange clients
3. Custom domain (once purchased)
4. Stripe/PayPal integration (once account set up)

## Key Decisions
- Three-platform split: Netlify (frontend), Railway (backend+DB+Redis), GitHub (code)
- Tailwind v4 (Vite plugin, CSS-first config)
- Shared trader handles all active users (scales better on single Railway instance)
- Redis pub/sub for signals, heartbeats, bot control, bot logs; Redis lists for cached status + rate limits
- bcrypt direct (no passlib) to avoid slim-image compat issues
- Fernet (AES-256) for key encryption — symmetric, no DB schema changes
- JWT over session cookies (stateless, SPA-friendly)
- Nullable `user_id` on Signal/Position/Trade so existing data survives
- ethers + @solana/web3.js direct (not wagmi/Web3Modal) to avoid massive dep tree
- SIWE for wallet ownership verification (ECDSA for EVM, ed25519 for Solana)
- MEXC key validation via `validate_credentials()` on save — catches fake keys immediately

## Critical Context
- Backend: `https://mexc-trading-bot-production-c215.up.railway.app/health`
- Frontend: `https://mexc-trading-bot.netlify.app`
- Analyst alive, trader alive, mode: live
- Railway services: mexc-trading-bot (FastAPI), analyst (signal gen), trader (multi-tenant executor)
- 8 strategies: RSI, MACD cross, EMA trend, volume breakout, Bollinger squeeze, Supertrend, ADX, Ichimoku
- MEXC API keys are now validated on save — fake keys rejected with 400 error
- Live bot start blocked if MEXC keys not verified
- 22 frontend pages, all code-split (largest chunk 336KB)
- CI/CD ready: GitHub Actions test + deploy workflows
- Email templates: 4 branded HTML templates for verification, reset, welcome, trade alerts
