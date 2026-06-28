<div align="center">
  <h1>NexTrade AI</h1>
  <p>Multi-exchange algorithmic trading platform — MEXC, Binance, Bybit</p>
  <p>
    <a href="https://mexc-trading-bot-production-c215.up.railway.app/health">
      <img src="https://img.shields.io/badge/backend-online-success?style=flat-square" alt="Backend">
    </a>
    <a href="https://dist-rho-sandy-41.vercel.app">
      <img src="https://img.shields.io/badge/frontend-deployed-blue?style=flat-square" alt="Frontend">
    </a>
    <img src="https://img.shields.io/badge/python-3.12-blue?style=flat-square" alt="Python 3.12">
    <img src="https://img.shields.io/badge/react-19-61DAFB?style=flat-square" alt="React 19">
    <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square" alt="FastAPI">
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License">
    <img src="https://img.shields.io/badge/strategies-15-orange?style=flat-square" alt="15 Strategies">
    <img src="https://img.shields.io/badge/tests-55%20passing-brightgreen?style=flat-square" alt="55 Tests Passing">
  </p>
</div>

---

## Overview

NexTrade AI is a production-grade algorithmic trading platform supporting **MEXC, Binance, and Bybit** exchanges. It features an autonomous market analyst that generates signals across **40 trading pairs** using **15 strategies**, a multi-tenant trader that executes positions per user via Redis pub/sub, and a full SaaS web dashboard with JWT authentication, encrypted API key storage, and plan-based access control.

The system has undergone a comprehensive safety audit against production failure scenarios: exchange credential errors, fake balance fallbacks, restart position recovery, SL/TP reconciliation, order ID traceability, and exchange-side fee extraction.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                      │
│  React 19 + Tailwind v4 + Recharts + React Query         │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS / JWT
┌────────────────────▼────────────────────────────────────┐
│                   Backend (Railway)                       │
│  FastAPI + SQLAlchemy async + Redis pub/sub               │
│  JWT auth · Plan enforcement · Rate limiting              │
│  Encrypted exchange key storage (Fernet AES-256)          │
│  Stripe subscriptions · GDPR compliance                   │
└──────┬──────────────────────────────┬───────────────────┘
       │ Redis pub/sub                │ Redis pub/sub
┌──────▼──────────┐          ┌───────▼───────────────────┐
│  Analyst Bot    │          │     Trader Bot (Railway)   │
│  · 15 strategies│ signals  │  · Multi-tenant sessions   │
│  · Signal gen   │────────► │  · Per-user exchange clients│
│  · Heartbeat    │          │  · Paper + Live execution  │
└─────────────────┘          │  · Risk management         │
                             │  · Position tracking        │
                             │  · Telegram/Email alerts    │
                             └────────────────────────────┘
```

### Services

| Service | Stack | Hosting |
|---------|-------|---------|
| **Frontend** | React 19, TypeScript, Tailwind v4, Recharts | Vercel |
| **Backend API** | FastAPI, SQLAlchemy (async), PostgreSQL, Redis | Railway |
| **Analyst Bot** | Python, pandas_ta, ccxt, Redis pub/sub | Railway |
| **Trader Bot** | Python, ccxt, Redis pub/sub, multi-tenant | Railway |
| **Database** | PostgreSQL (prod) / SQLite (dev) | Railway |
| **Cache** | Redis — signals, heartbeats, logs, rate limits | Railway |

## Production Safety (Audited)

All critical failure modes from independent code audits have been addressed:

| Category | Fix |
|----------|-----|
| **Fake balance** | Replaced hardcoded `$10,000` with live `exchange.fetch_balance()` via `_get_live_balance()` |
| **Restart recovery** | `recover_positions()` seeds `PositionTracker` from exchange on startup |
| **SL/TP tracking** | `reconcile_positions()` live-diffs exchange positions vs local tracker every cycle |
| **Order traceability** | UUIDv4 `clientOrderId` on every order; `exchange_order_id` column persisted to DB |
| **Fee extraction** | Real fee from `create_order` response `fee.cost`; 0.1% fallback for paper mode |
| **Credential errors** | All 3 exchange clients surface actual error messages (no silent bare `except`) |
| **Min notional** | `_validate_order()` rejects orders below `$5` notional |
| **Hard cap** | 50 concurrent position limit enforced |
| **Balance snapshots** | Per-user equity tracked to Redis every 15 seconds |
| **Circuit breaker** | Drawdown-based trading halt in `RiskManager` |

## Features

### Trading Engine
- **15 strategies**: RSI, MACD cross, EMA trend, Volume breakout, Bollinger squeeze, Supertrend, ADX, Ichimoku, Pullback, Range, CounterTrend, StochRSI, PSAR, MFI, VWAP
- **Multi-timeframe analysis**: 15m, 1h, 4h with configurable signal resolution
- **Paper trading** with realistic fill simulation (slippage, spread)
- **Live trading** via MEXC, Binance, Bybit (spot + futures)
- **Risk management**: max position size, daily drawdown limits, circuit breaker, cooldown, configurable leverage
- **Per-user positions, signals, and trade history** stored in PostgreSQL

### SaaS Platform
- **JWT authentication** with bcrypt password hashing (24h token expiry)
- **Three subscription tiers**: Basic ($29), Pro ($79), Enterprise ($199)
- **Plan enforcement**: per-tier limits on pairs, bots, position size, and trade type
- **Encrypted API key storage**: Fernet AES-256 at rest
- **Multi-tenant trader**: shared executor with per-user isolated sessions
- **Stripe subscription management**: checkout, webhook, billing portal, plan sync
- **Real-time bot control** via Redis pub/sub (no polling delay)
- **Rate limiting**: token bucket per user (60 requests/min)
- **Admin panel**: user management, plan overview, key status

### Monitoring
- **Analyst + Trader health monitoring** via Redis heartbeats
- **Real-time bot logs** streamed to Redis, visible in dashboard
- **Equity curve chart** with Recharts (auto-updating)
- **P&L tracking**, win rate, trade history
- **Notifications**: Telegram + Email (SMTP)
- **Strategy performance**: per-strategy win rate, P&L, signal count
- **Portfolio view**: aggregate P&L, pair breakdown, unrealized P&L
- **CSV export**: streaming CSV for trades and positions

### Platform Features
- **Code splitting**: All routes lazily loaded via `React.lazy` + `Suspense`
- **Dark/light mode**: `ThemeContext` with localStorage persistence
- **Toast notifications**: auto-dismiss (4s), 4 types, animated
- **Loading skeletons**: `Skeleton`, `TableSkeleton`, `CardSkeleton`
- **Error boundaries**: `ErrorBoundary` wrapping all routes with retry button
- **Sortable tables**: `SortableTable<T>` with click-to-sort headers
- **Real-time updates**: WebSocket endpoint (`/ws`) with JWT auth + REST polling fallback
- **Free trial**: trial period per user with expiry enforcement

### Account Features
- **Crypto wallet auth**: SIWE (EIP-4361) for EVM (MetaMask) + Solana (Phantom)
- **Email verification**: token-based verification on registration
- **Password reset**: forgot/reset password flow with email
- **Withdrawal protection**: address whitelist + time-delayed withdrawals
- **User API keys**: generate/revoke keys for programmatic API access
- **GDPR compliance**: data export (full JSON) + account deletion
- **Backtesting UI**: pair + strategy + period selectors
- **Admin analytics**: user growth, plan breakdown, active bots, total P&L

### Trust & Transparency
- **Real social proof**: Landing page displays live user count and total trades from DB
- **Terms of Service**, **Privacy Policy**, **Whitepaper**, **Security**, **Changelog**, **About** pages
- **Registered company**: NexTrade AI Ltd., Larnaca, Cyprus
- **SLA commitment**: Best-effort uptime across all plans

## Subscription Plans

| Feature | Basic ($29) | Pro ($79) | Enterprise ($199) |
|---------|------------|-----------|-------------------|
| Concurrent bots | 1 | 3 | Unlimited |
| Trading pairs | 3 | 10 | Unlimited |
| Max position | $500 | $5,000 | Unlimited |
| Spot trading | ✅ | ✅ | ✅ |
| Futures trading | ❌ | ✅ | ✅ |
| API access | ✅ | ✅ | ✅ |

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- Redis 7+
- Exchange API keys (MEXC, Binance, or Bybit)

### 1. Clone & Setup

```bash
git clone https://github.com/abeermeer/Nextrade-trading-bot.git
cd mexc-trading-bot
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt && pip install -e .
cd frontend && npm install && cd ..
```

### 2. Configure

```bash
cp config/.env.example config/.env
# Edit config/.env with your exchange API keys
```

### 3. Run

```bash
# Start all services (requires Docker)
docker-compose up --build

# Or run individually:
# Terminal 1: uvicorn web.main:app --reload --port 8000
# Terminal 2: python scripts/run_analyst.py
# Terminal 3: python scripts/run_trader.py
# Terminal 4: cd frontend && npm run dev
```

## Testing

```bash
# Run backend tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=term
```

## Deployment

| Component | Platform | Method |
|-----------|----------|--------|
| Frontend | **Vercel** | `cd frontend && npm run build && vercel deploy dist --prod` |
| Backend API | **Railway** | Auto-deploys from GitHub master via Dockerfile.web |
| Analyst Bot | **Railway** | Auto-deploys from GitHub master via Dockerfile.analyst |
| Trader Bot | **Railway** | Auto-deploys from GitHub master via Dockerfile.trader |
| PostgreSQL | **Railway** | Managed add-on, shared across all services via `DATABASE_URL` |
| Redis | **Railway** | Managed add-on, must be attached to all 3 services |

## License

MIT
