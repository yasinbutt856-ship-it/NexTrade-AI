import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from db.models import Base, SignalRecord, PositionRecord, TradeRecord, SignalActionDB, OrderSideDB, OrderStatusDB, BotModeDB
from shared.models import Signal, SignalAction, StrategyResult


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_save_and_query_signal(db_session):
    record = SignalRecord(
        symbol="BTC/USDT",
        action=SignalActionDB.buy,
        confidence=0.85,
        price=50000.0,
        timeframe="1h",
        strategy_results=[{"strategy_name": "rsi", "action": "buy", "confidence": 0.8}],
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(record)
    await db_session.commit()

    result = await db_session.execute(
        select(SignalRecord).order_by(desc(SignalRecord.created_at)).limit(1)
    )
    r = result.scalar_one()
    assert r.symbol == "BTC/USDT"
    assert r.action == SignalActionDB.buy
    assert r.confidence == 0.85
    assert r.timeframe == "1h"


@pytest.mark.asyncio
async def test_save_trade(db_session):
    record = TradeRecord(
        symbol="ETH/USDT",
        side=OrderSideDB.buy,
        price=3000.0,
        quantity=1.0,
        total=3000.0,
        fee=3.0,
        mode=BotModeDB.paper,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(record)
    await db_session.commit()

    result = await db_session.execute(
        select(TradeRecord).order_by(desc(TradeRecord.created_at)).limit(1)
    )
    r = result.scalar_one()
    assert r.symbol == "ETH/USDT"
    assert r.side == OrderSideDB.buy
    assert r.total == 3000.0
    assert r.mode == BotModeDB.paper


@pytest.mark.asyncio
async def test_signal_actions_enum():
    assert SignalActionDB.buy.value == "buy"
    assert SignalActionDB.sell.value == "sell"
    assert SignalActionDB.hold.value == "hold"


@pytest.mark.asyncio
async def test_position_record_creation(db_session):
    record = PositionRecord(
        symbol="SOL/USDT",
        side=OrderSideDB.buy,
        entry_price=100.0,
        current_price=110.0,
        quantity=5.0,
        unrealized_pnl=50.0,
        status=OrderStatusDB.open,
        mode=BotModeDB.paper,
        opened_at=datetime.now(timezone.utc),
    )
    db_session.add(record)
    await db_session.commit()

    result = await db_session.execute(
        select(PositionRecord).where(PositionRecord.symbol == "SOL/USDT")
    )
    p = result.scalar_one()
    assert p.quantity == 5.0
    assert p.unrealized_pnl == 50.0
