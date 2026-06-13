from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import async_session_factory
from db.models import SignalRecord, PositionRecord, TradeRecord, SignalActionDB, OrderSideDB, OrderStatusDB, BotModeDB
from shared.models import Signal, Position, BotMode


async def save_signal(signal: Signal, timeframe: Optional[str] = None) -> None:
    async with async_session_factory() as session:
        record = SignalRecord(
            symbol=signal.symbol,
            action=SignalActionDB(signal.action.value),
            confidence=signal.confidence,
            price=signal.price,
            timeframe=timeframe,
            strategy_results=[r.model_dump(mode="json") for r in signal.strategy_results],
            signal_metadata=signal.metadata,
            created_at=datetime.now(timezone.utc),
        )
        session.add(record)
        await session.commit()


async def save_trade(
    symbol: str,
    side: str,
    price: float,
    quantity: float,
    fee: float = 0.0,
    pnl: Optional[float] = None,
    mode: str = "paper",
) -> None:
    async with async_session_factory() as session:
        record = TradeRecord(
            symbol=symbol,
            side=OrderSideDB(side),
            price=price,
            quantity=quantity,
            total=price * quantity,
            fee=fee,
            pnl=pnl,
            mode=BotModeDB(mode),
            created_at=datetime.now(timezone.utc),
        )
        session.add(record)
        await session.commit()


async def save_position(position: Position, mode: str = "paper") -> None:
    async with async_session_factory() as session:
        record = PositionRecord(
            symbol=position.symbol,
            side=OrderSideDB(position.side.value),
            entry_price=position.entry_price,
            current_price=position.current_price,
            quantity=position.quantity,
            unrealized_pnl=position.unrealized_pnl,
            realized_pnl=position.realized_pnl,
            stop_loss=position.stop_loss,
            take_profit=position.take_profit,
            status=OrderStatusDB(position.status.value),
            mode=BotModeDB(mode),
            opened_at=position.opened_at,
            closed_at=position.closed_at,
        )
        session.add(record)
        await session.commit()
