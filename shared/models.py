from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SignalAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


class OrderStatus(str, Enum):
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class BotMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"


class StrategyResult(BaseModel):
    strategy_name: str
    action: SignalAction
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict = {}


class Signal(BaseModel):
    symbol: str
    action: SignalAction
    confidence: float = Field(ge=0.0, le=1.0)
    price: float
    timestamp: datetime
    strategy_results: list[StrategyResult] = []
    metadata: dict = {}


class Position(BaseModel):
    id: str
    symbol: str
    side: OrderSide
    entry_price: float
    current_price: float
    quantity: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None
    status: OrderStatus = OrderStatus.OPEN


class ExchangeConfig(BaseModel):
    name: str = "mexc"
    use_sandbox: bool = False
    rate_limit_per_second: int = 20


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    signal_channel: str = "signals:market"
    heartbeat_channel: str = "heartbeat:analyst"
    db: int = 0


class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "json"
    file: str = "logs/trading.log"
    max_bytes: int = 10485760
    backup_count: int = 5
    error_file: str = "logs/error.log"


class DashboardConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    username: str = "admin"
    password_env_var: str = "DASHBOARD_PASSWORD"
    session_secret_env_var: str = "DASHBOARD_SECRET"


class Config(BaseModel):
    exchange: ExchangeConfig = ExchangeConfig()
    redis: RedisConfig = RedisConfig()
    logging: LoggingConfig = LoggingConfig()
    dashboard: DashboardConfig = DashboardConfig()
