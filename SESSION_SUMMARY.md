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
- **Full frontend**: Landing, Login/Signup, Dashboard (bot viz, stats, equity curve, logs, wallet), Settings (keys, wallet, mode/type, risk), Admin (user mgmt), Positions/Signals/Trades — all dark themed
- **Netlify 404**: `public/_redirects` → `/* /index.html 200`
- **Multi-tenant trader**: per-user UserSession with PaperEngine/RiskManager/PositionTracker/MEXCClient, signal execution per user_id
- **DB**: `user_id` on SignalRecord/PositionRecord/TradeRecord (nullable, indexed), wallet_address + wallet_type on UserRecord
- **MEXC Futures**: `set_leverage()`, `set_position_mode()`, `market="swap"` for futures orders
- **Plan enforcement**: `shared/plan_limits.py` — tier limits enforced on settings + registration
- **Real-time bot control**: Redis pub/sub — start/stop instantly creates/removes sessions
- **Dashboard additions**: Recharts equity curve AreaChart, bot log viewer (Redis `logs:bot`, GET /api/logs, 5s poll)
- **Rate limiting**: Token bucket (60 req/min) via RateLimitMiddleware on /api/*
- **Mobile responsive**: `overflow-x-auto` nav on small screens
- **64 unit tests** passing (18 new: plan_limits, auth bcrypt/JWT, encryption Fernet)
- **Repo cleanup**: Professional README (arch diagram, API ref, setup), MIT LICENSE, .env.example, frontend README
- **Wallet (EVM + Solana)**: `shared/wallet.py` (SIWE nonce, eth_account recover, nacl verify), endpoints (nonce, wallet-login, wallet-link, PUT/GET/DELETE wallet), WalletContext.tsx (ethers + @solana/web3.js), WalletConnect.tsx (MetaMask + Phantom buttons), wallet in Settings + Dashboard
- **Landing page redesigned**: Hero with animated terminal sim (analyst+trader flow), gradient orbs, floating stat cards (24/7), social proof (real user count from DB); "How It Works" 3-step with connector lines; Features grid (6 cards, hover glow); Trust & Security section (6 items); Pricing (3 tiers, Pro highlighted); FAQ accordion (6 questions); CTA + company footer with Terms/Privacy/Whitepaper links
- **Deployed**: Latest build live on Netlify (`https://mexc-trading-bot.netlify.app`), Railway backend healthy (`{"status":"ok"}`)

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
- No Stripe/PayPal yet — signup free for all plans, wallet ready for future crypto payments

## Completed This Session
- **Real social proof from DB**: Added `GET /api/stats` endpoint returning `total_users`, `weekly_users`, `total_trades`, `win_rate` from DB. Landing hero now shows real counts instead of hardcoded "2,400+". CTA section pulls from live data.
- **Removed fake metrics**: Removed floating "87% Win Rate" card from `HeroIllustration`. All displayed stats now come from actual DB queries.
- **Terms of Service page** (`/terms`): 9 sections (Acceptance, Registration, Fees, Trading Risks, API Key Security, IP, Liability, Termination, Governing Law) — NexTrade AI, Larnaca, Cyprus
- **Privacy Policy page** (`/privacy`): 7 sections — AES-256 encryption, no data selling, encrypted API keys
- **Whitepaper page** (`/whitepaper`): Deep-dive on all 8 strategies (RSI, MACD, EMA, Volume, Bollinger, Supertrend, ADX, Ichimoku) + architecture (Redis pub/sub flow) + risk management (circuit breaker, trailing stop-loss, position sizing, cooldown)
- **Company identity in footer**: 3-column grid (brand description, company links to Terms/Privacy/Whitepaper/Docs, contact info — support@nextrade.ai, Larnaca, Cyprus). Real links replace plain text.
- **Support email in Navbar**: `Support` mailto: link in Navbar for anonymous users, plus `support@nextrade.ai` in footer contact section
- **About page** (`/about`): Mission, development timeline (2025 Q3 → 2026 Q2), architecture overview (Analyst + Trader via Redis), team (Abeer Meer), company info (NexTrade AI Ltd., Larnaca, Cyprus)
- **GitHub repo polish**: Description, homepage URL (`https://mexc-trading-bot.netlify.app`), 7 topics set via `gh repo edit`; README updated with Trust & Transparency section + `/api/stats` in API reference
- **Frontend builds clean** (zero errors), pushed to GitHub, deployed to Netlify + Railway

## Remaining
1. Custom domain (`.netlify.app` subdomain kills trust — #1 priority)
2. Stripe/PayPal payment integration + checkout flow
3. Multi-exchange support (Binance, Bybit, etc.)

## Critical Context
- Backend: `https://mexc-trading-bot-production-c215.up.railway.app/health`
- Frontend: `https://mexc-trading-bot.netlify.app`
- Analyst alive, trader alive, mode: live
- Railway services: mexc-trading-bot (FastAPI), analyst (signal gen), trader (multi-tenant executor)
- 8 strategies: RSI, MACD cross, EMA trend, volume breakout, Bollinger squeeze, Supertrend, ADX, Ichimoku
- `create_redis_client()` checks `REDIS_URL` env var first, falls back to YAML
- PostgreSQL auto-convert: `postgres://` → `postgresql+asyncpg://`
- Fernet cipher lazy init — uses `ENCRYPTION_KEY` env var or random key
- Docker Desktop not running locally; all via Railway + Netlify
- `docker-compose.yml` available for local dev
- Root: `C:\Users\brosp\Downloads\mexc-trading-bot`
