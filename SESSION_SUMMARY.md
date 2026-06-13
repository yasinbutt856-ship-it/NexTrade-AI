# Trading Bot System — Session Summary

## Project: MEXC Enterprise Trading Bot

### Goal
Two-bot system: **Market Analyst** (generates trading signals) + **Trader Bot** (executes on MEXC spot & futures). Fully autonomous, enterprise-grade, paper + live modes.

### Tech Stack (Decided)
| Component | Choice |
|---|---|
| Language | Python 3.12 |
| Exchange | MEXC via CCXT |
| Finance Data | yfinance (primary) + CoinGecko (backup) — free, no API keys |
| Bot Communication | Redis pub/sub |
| Config | YAML + .env |
| Data Models | Pydantic v2 |
| TA Indicators | pandas-ta |
| Logging | structlog |
| Dashboard | FastAPI + Jinja2 |
| Scheduling | APScheduler |
| DB | SQLite (dev) → PostgreSQL (prod) |
| Testing | pytest + mocked CCXT |
| Deployment | Docker + docker-compose |

### Architecture
```
Analyst Bot → Redis (signals:market) → Trader Bot → MEXC (or PaperEngine)
                                  ↓
                          Dashboard + DB
```

### Key Features (Planned)
- Spot + Futures trading (isolated & cross margin)
- Paper mode (simulated fills, virtual P&L)
- Live mode (real orders via CCXT)
- 5 strategies: RSI, MACD cross, EMA trend, Volume breakout, Bollinger squeeze
- Weighted signal scoring with confidence
- Risk management: position sizing, daily drawdown, circuit breaker, cooldowns
- SL/TP automatically attached to orders
- Full audit trail in DB
- Web dashboard for monitoring

### Project Structure (Planned)
```
mexc-trading-bot/
├── config/           # settings.yaml, strategies.yaml, .env
├── analyst/          # DataFetcher, Indicators, Strategies, SignalGenerator
├── trader/           # Executor, RiskManager, PositionTracker, Exchange/
├── shared/           # Models, ConfigLoader, RedisClient, Logger
├── web/              # FastAPI dashboard
├── db/               # SQLAlchemy models + Alembic migrations
├── tests/            # pytest suite
├── scripts/          # Run scripts
├── docker-compose.yml
└── Dockerfile.*
```

### What to Build Next (Waiting for Instruction)
- [ ] Phase 1: Project scaffold, config, shared modules
- [ ] Phase 2: Analyst bot
- [ ] Phase 3: Trader bot
- [ ] Phase 4: Dashboard + DB
- [ ] Phase 5: Docker + deploy
- [ ] Phase 6: Tests

### Notes
- User has Python 3.12, Node 24, pip available
- Docker + Redis not installed yet — will use Docker images
- User will provide MEXC API key + secret
- User may also provide a finance API key if not using free sources
- Session date: 2026-06-14
