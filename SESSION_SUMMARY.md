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
- **Exchange key mgmt**: Fernet AES-256 encrypt via `shared/encryption.py`, PUT endpoint only (no GET — keys never returned to client)
- **User settings API**: paper/live, spot/futures, max_position, bot start/stop via Redis pub/sub `bot:control`
- **Admin user list**: GET /api/user/admin/users — all users with plan/mode/bot_active/key status
- **Full frontend**: 22 pages — Landing, Login, Signup, VerifyEmail, ForgotPassword, ResetPassword, Dashboard, Settings, Admin, AdminAnalytics, Positions, Signals, Trades, StrategyPerformance, Backtesting, Status, Docs, Terms, Privacy, Whitepaper, About, Changelog, Security — all dark themed with code splitting
- **Multi-tenant trader**: per-user UserSession with PaperEngine/RiskManager/PositionTracker/exchange clients, signal execution per user_id
- **Wallet (EVM + Solana)**: SIWE nonce, eth_account recover, nacl verify; endpoints + WalletContext + WalletConnect (MetaMask + Phantom)
- **Plan enforcement**: `shared/plan_limits.py` — tier limits + usage caps + trial enforcement
- **18+ revenue-ready features**: strategy perf, portfolio, CSV export, backtesting UI, custom pairs, notification prefs, user API keys, admin analytics, trial status, usage tracking, GDPR export/delete
- **Platform depth**: code splitting (336KB max), dark/light mode, toast notifications, loading skeletons, error boundaries, sortable tables, WebSocket real-time
- **7 trust pages**: Terms, Privacy, Whitepaper, Security, Changelog, About, Status — plus company footer, support email, SLA commitment
- **64 backend tests passing**, frontend test setup (vitest + testing-library)
- **README**: fully updated with all API endpoints, full project structure, all features

## Completed This Session (Jun 17 — Security + Quality Pass)

### 🔴 Security
1. **Decrypted key GET endpoints removed** — `GET /api/user/exchange-keys` and `GET /api/user/mexc-keys` deleted from `user_router.py`. Keys are no longer returned to the frontend (prevents XSS/leak). Frontend Settings form starts empty each visit. Key status shown via `keys_verified` in `/api/auth/me` response.
2. **Duplicate PUT /mexc-keys removed** — `PUT /api/user/mexc-keys` consolidated into `PUT /api/user/exchange-keys` which handles all exchanges (MEXC/Binance/Bybit) via the `exchange` field. `MexcKeysRequest` model removed. `updateMexcKeys`/`getMexcKeys` removed from frontend API client.
3. **WebSocket token expiry** — Server closes with code 4001 on auth failure. Client `useWebSocket` hook now checks `event.code`; if 4001, clears token and redirects to `/login` instead of infinite reconnect loop.

### 🟠 Performance
4. **Backtest event loop fix** — `yfinance.Ticker.history()` calls in `Backtester.fetch_data()` now run via `loop.run_in_executor()` so they don't block the async event loop. `fetch_data` changed from sync to `async def`.

### 🟡 Reliability
5. **GDPR deletion** — `DELETE /api/user/data-delete` now stops the bot (sets `bot_active=False`, publishes `bot:control` stop via Redis) before deleting records and anonymizing user.
6. **Admin seed moved** — `seed_admin()` function extracted from `auth_router.py` to `scripts/seed_admin.py`. Imported in `main.py` from new location.
7. **SLA claim softened** — Changed from "99.5% uptime" to "Best-effort uptime" in both README and Status.tsx to avoid legal exposure.

### 📝 Documentation
8. **README fixes** — Architecture diagram updated ("Encrypted MEXC key storage" → "Encrypted exchange key storage"). `GET /api/auth/me` moved from Public to User Endpoints (requires auth). `user_router.py` description updated ("MEXC keys" → "exchange keys"). Removed stale `(18 endpoints)` count from `platform_router.py` description.

### ✅ Files Changed (15)
- `web/user_router.py` — Removed 3 endpoints + MexcKeysRequest + unused `decrypt` import
- `web/auth_router.py` — Added `keys_verified` to UserResponse, removed seed_admin function
- `web/main.py` — Import seed_admin from scripts/seed_admin.py
- `web/platform_router.py` — GDPR now stops bot before deleting
- `backtest/backtester.py` — fetch_data async, yfinance in run_in_executor
- `scripts/seed_admin.py` — New file, extracted from auth_router
- `frontend/src/api/client.ts` — Removed getExchangeKeys, updateMexcKeys, getMexcKeys
- `frontend/src/types/index.ts` — Added keys_verified to UserProfile
- `frontend/src/context/AuthContext.tsx` — Added keys_verified to initial user state
- `frontend/src/pages/Settings.tsx` — Removed existingKeys query/effect, initializes from user.keys_verified
- `frontend/src/pages/Status.tsx` — SLA: Best-effort instead of 99.5%
- `frontend/src/hooks/useWebSocket.ts` — Close code 4001 → redirect to login
- `README.md` — 5 fixes (SLA, diagram, /me placement, descriptions)

## Remaining
1. Custom domain (once purchased)
2. Stripe/PayPal integration (once account set up)

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
- Keys never returned to client — prevents XSS/leak, Settings form starts empty
- WebSocket code 4001 redirects to login — prevents reconnect loop on expired token
- Best-effort SLA — avoids legal commitment on single-instance Railway deployment

## Critical Context
- Backend: `https://mexc-trading-bot-production-c215.up.railway.app/health`
- Frontend: `https://mexc-trading-bot.netlify.app`
- Analyst alive, trader alive, mode: live
- Railway services: mexc-trading-bot (FastAPI), analyst (signal gen), trader (multi-tenant executor)
- 8 strategies: RSI, MACD cross, EMA trend, volume breakout, Bollinger squeeze, Supertrend, ADX, Ichimoku
- Exchange API keys validated on save — fake keys rejected with 400 error
- Keys NOT returned via any GET endpoint (security)
- Live bot start blocked if keys not verified
- 22 frontend pages, all code-split (largest chunk 336KB)
- CI/CD ready: GitHub Actions test + deploy workflows
- Email templates: 4 branded HTML templates for verification, reset, welcome, trade alerts
