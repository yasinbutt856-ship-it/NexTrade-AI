# Trading Bot System — Session Summary

## Project: MEXC Enterprise Trading Bot

### Goal
Two-bot system: **Market Analyst** (generates trading signals) + **Trader Bot** (executes on MEXC spot & futures). Fully autonomous, enterprise-grade, paper + live modes.

### Tech Stack
| Component | Choice | Status |
|---|---|---|
| Language | Python 3.12 | ✅ |
| Exchange | MEXC via CCXT | ✅ |
| Realtime Data | ccxt.pro WebSocket | ✅ |
| Finance Data | yfinance (primary) + CoinGecko (backup) | ✅ |
| Bot Communication | Redis pub/sub (Railway Redis) | ✅ |
| Config | YAML + .env | ✅ |
| Data Models | Pydantic v2 | ✅ |
| TA Indicators | pandas_ta | ✅ |
| Logging | structlog with rotation + stdout | ✅ |
| Dashboard | React + Vite + TypeScript (Netlify) | ✅ |
| Backend API | FastAPI (Railway) | ✅ |
| DB | SQLite (dev) / Redis cache (prod) | ✅ |
| Testing | pytest (46 tests) | ✅ |
| Deployment | Railway (3 services) | ✅ |
| Notifications | Telegram + Email | ✅ |

### Architecture
```
Analyst Bot (Railway) ──redis──► Trader Bot (Railway) ──► PaperEngine
                                      │
          Frontend (Netlify) ◄── FastAPI (Railway) ◄──────┘
```

### Completed Phases

#### Phase 1 — Project Scaffold ✅
- `pyproject.toml` with all dependencies
- `config/settings.yaml` — full bot configuration
- `config/strategies.yaml` — 5 strategies with weights + resolution mode
- `config/.env.example` — API keys template
- `shared/models.py` — Pydantic v2 models
- `shared/config_loader.py` — YAML + .env loader
- `shared/redis_client.py` — Async Redis pub/sub with heartbeat, list cache
- `shared/logger.py` — structlog with rotation + stdout for Railway
- `shared/rate_limiter.py` — Token-bucket rate limiter
- Dockerfiles + docker-compose.yml
- `.gitignore` + git init

#### Phase 2 — Analyst Bot ✅
- `analyst/data_fetcher.py` — yfinance + CoinGecko fallback with tenacity retry
- `analyst/indicator_calculator.py` — All TA indicators via pandas_ta
- `analyst/pair_selector.py` — Dynamic top-N pairs by volume (CCXT), fallback list
- `analyst/signal_aggregator.py` — Weighted / Strict / Majority modes
- `analyst/strategy_runner.py` — Runs all 5 enabled strategies
- `analyst/analyst_bot.py` — Orchestrator: heartbeat loop + signal generation cycle + Redis cache
- `analyst/strategies/` — RSI, MACD, EMA Trend, Volume Breakout, Bollinger Squeeze

#### Phase 3 — Trader Bot ✅
- `trader/paper_engine.py` — Simulated fills, virtual P&L, SL/TP triggers, partial fills
- `trader/exchange/mexc_client.py` — MEXC spot + futures via CCXT with rate limiter
- `trader/risk_manager.py` — Position sizing, daily drawdown, circuit breaker, cooldowns
- `trader/position_tracker.py` — Open/closed positions, unrealized/realized P&L
- `trader/notifier.py` — Telegram + Email notifications
- `trader/trader_bot.py` — Full orchestrator: subscribe → risk check → paper/live execute → track → notify

#### Phase 4 — Dashboard API + DB ✅
- FastAPI with 8 API endpoints (reads signals from Redis cache)
- SQLAlchemy ORM + Alembic migrations (SQLite)
- DB persistence wired into analyst + trader bots
- React frontend with 7 views

#### Phase 5 — Docker Polish ✅
- Multi-stage Dockerfiles with layer caching
- docker-compose.yml (redis + analyst + trader + web)
- docker-compose.override.yml (hot reload for dev)
- `.dockerignore`

#### Phase 6 — Realtime Data + Tests ✅
- `shared/realtime_data.py` — ccxt.pro WebSocket manager
- Ticker watchers + OHLCV watchers (per-symbol per-timeframe concurrent via gather)
- Price callbacks update PositionTracker (PnL) and PaperEngine (SL/TP) in real-time
- 46 tests total, all passing

### Project Structure
```
mexc-trading-bot/
├── config/
│   ├── settings.yaml
│   ├── strategies.yaml
│   └── .env.example
├── shared/
│   ├── models.py
│   ├── config_loader.py
│   ├── redis_client.py
│   ├── logger.py
│   ├── rate_limiter.py
│   └── realtime_data.py
├── analyst/
│   ├── data_fetcher.py
│   ├── indicator_calculator.py
│   ├── pair_selector.py
│   ├── signal_aggregator.py
│   ├── strategy_runner.py
│   ├── analyst_bot.py
│   └── strategies/
│       ├── base.py
│       ├── rsi_strategy.py
│       ├── macd_strategy.py
│       ├── ema_trend_strategy.py
│       ├── volume_breakout_strategy.py
│       └── bollinger_squeeze_strategy.py
├── trader/
│   ├── paper_engine.py
│   ├── risk_manager.py
│   ├── position_tracker.py
│   ├── notifier.py
│   ├── trader_bot.py
│   └── exchange/
│       └── mexc_client.py
├── frontend/
│   └── src/
│       ├── pages/ (7 views)
│       ├── components/Layout.tsx
│       ├── api/client.ts
│       └── types/index.ts
├── web/
│   ├── main.py
│   └── routers.py
├── db/
│   ├── models.py
│   ├── database.py
│   ├── repository.py
│   └── migrations/
├── tests/
│   ├── test_analyst.py (9)
│   ├── test_trader.py (16)
│   ├── test_db.py (4)
│   ├── test_integration.py (6)
│   └── test_realtime.py (11)
├── scripts/
│   ├── run_analyst.py
│   └── run_trader.py
├── Dockerfile.analyst
├── Dockerfile.trader
├── Dockerfile.web
├── docker-compose.yml
├── docker-compose.override.yml
├── .dockerignore
├── pyproject.toml
├── requirements.txt
├── alembic.ini
└── .gitignore
```

### Tests
- **46 total tests**, all passing
- `pytest tests/ -v` to run
- `pytest --cov=shared,analyst,trader,db,web tests/` for coverage

### Deployment (2026-06-14)

| Service | Platform | URL |
|---------|----------|-----|
| Code | GitHub | https://github.com/abeeruniversity/mexc-trading-bot |
| Frontend | Netlify | https://funny-cobbler-d51629.netlify.app |
| Backend API | Railway | https://mexc-trading-bot-production-c215.up.railway.app |
| Analyst Bot | Railway | Internal service (no public URL) |
| Trader Bot | Railway | Internal service (no public URL) |
| Redis | Railway | Internal plugin on `redis.railway.internal:6379` |

### Railway Project
- **Project**: `poetic-bravery`
- **Services**: `mexc-trading-bot` (FastAPI), `analyst`, `trader`
- **Databases**: `Redis` (plugin)
- **All services Online**, signals flowing, analyst alive

### Fixes Applied
- `pandas_ta` pinned to `0.4.71b0` (pre-release version, was failing in Docker build)
- CORS updated to allow Netlify frontend + Railway domain
- Dockerfile.web uses `$PORT` env var for Railway compatibility
- `create_redis_client()` helper supports `REDIS_URL` env var
- Stdout log handler added for Railway log capture
- `numpy.bool` serialization fixed in Bollinger strategy + `_json_safe` helper in repository
- Signals cached in Redis list (`signals:recent`) for cross-service API access
- `RedisClient` extended with `rpush`, `lrange`, `ltrim` methods
- Debug `print()` statements added for container startup diagnostics

### What's Next
- PostgreSQL migration (optional) — for shared DB persistence
- Custom domain on Netlify (optional)
- Start bots from standby to active trading mode
