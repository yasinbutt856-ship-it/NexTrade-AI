import asyncio
import signal
from datetime import datetime, timezone, timedelta
from typing import Optional

from db.repository import save_trade, save_position
from shared.config_loader import ConfigLoader
from shared.logger import get_logger
from shared.models import (
    BotMode,
    Signal,
    SignalAction,
    OrderSide,
    OrderType,
)
from shared.realtime_data import RealtimeDataManager
from shared.redis_client import RedisClient
from trader.paper_engine import PaperEngine
from trader.exchange.mexc_client import MEXCClient
from trader.risk_manager import RiskManager
from trader.position_tracker import PositionTracker
from trader.notifier import Notifier

logger = get_logger(__name__)


class TraderBot:
    def __init__(
        self,
        config_loader: ConfigLoader,
        redis_client: RedisClient,
    ):
        self.config_loader = config_loader
        self.redis = redis_client
        self.settings = config_loader.load_settings()
        self._running = False
        self._standby = True
        self._last_heartbeat: Optional[datetime] = None
        self._last_signal_time: Optional[datetime] = None

        trader_cfg = self.settings.get("trader", {})
        bot_cfg = self.settings.get("bot", {})
        redis_cfg = self.settings.get("redis", {})
        exchange_cfg = self.settings.get("exchange", {})

        self.mode = BotMode(bot_cfg.get("mode", "paper"))
        self.signal_channel = redis_cfg.get("signal_channel", "signals:market")
        self.heartbeat_channel = redis_cfg.get("heartbeat_channel", "heartbeat:analyst")
        self.stale_signal_timeout = trader_cfg.get("stale_signal_timeout_seconds", 300)
        self.heartbeat_timeout = 60

        self.position_tracker = PositionTracker()
        self.risk_manager = RiskManager(
            max_position_size_usdt=trader_cfg.get("max_position_size_usdt", 1000),
            max_daily_drawdown_pct=trader_cfg.get("max_daily_drawdown_pct", 5.0),
            circuit_breaker_drawdown_pct=trader_cfg.get("circuit_breaker_drawdown_pct", 10.0),
            cooldown_seconds=trader_cfg.get("cooldown_seconds", 300),
        )
        self.paper_engine = PaperEngine()
        self.notifier = Notifier(
            telegram_token=self.config_loader.get_env("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=self.config_loader.get_env("TELEGRAM_CHAT_ID"),
            smtp_host=self.config_loader.get_env("SMTP_HOST"),
            smtp_port=int(self.config_loader.get_env("SMTP_PORT", "587")),
            smtp_user=self.config_loader.get_env("SMTP_USER"),
            smtp_password=self.config_loader.get_env("SMTP_PASSWORD"),
            email_from=self.config_loader.get_env("EMAIL_FROM"),
            email_to=self.config_loader.get_env("EMAIL_TO"),
        )
        self.exchange: Optional[MEXCClient] = None
        if self.mode == BotMode.LIVE:
            self.exchange = MEXCClient(
                api_key=self.config_loader.get_env("MEXC_API_KEY", ""),
                api_secret=self.config_loader.get_env("MEXC_API_SECRET", ""),
                use_sandbox=exchange_cfg.get("use_sandbox", False),
            )

        self._ws_started = False
        self._realtime: Optional[RealtimeDataManager] = None
        ws_key = self.config_loader.get_env("MEXC_API_KEY", "")
        ws_secret = self.config_loader.get_env("MEXC_API_SECRET", "")
        if ws_key and ws_secret:
            self._realtime = RealtimeDataManager(api_key=ws_key, api_secret=ws_secret)
            self._realtime.on_price(self._on_price_update)

    async def _on_price_update(self, symbol: str, price: float) -> None:
        self.position_tracker.update_price(symbol, price)
        await self.paper_engine.update_price(symbol, price)

    async def start(self) -> None:
        self._running = True
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
            except NotImplementedError:
                pass

        print("DEBUG: Connecting to Redis...", flush=True)
        await self.redis.connect()
        print("DEBUG: Redis connected", flush=True)

        if self._realtime:
            asyncio.create_task(self._realtime.start(
                symbols=["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"],
            ))

        logger.info(
            "trader_bot_started",
            mode=self.mode.value,
            standby=True,
        )

        monitor_task = asyncio.create_task(self._monitor_loop())
        await self.redis.subscribe(self.signal_channel, self._handle_signal)
        await monitor_task

    async def stop(self) -> None:
        self._running = False
        logger.info("trader_bot_shutting_down")

        if self.mode == BotMode.LIVE:
            try:
                await self.exchange.cancel_all_orders()
                logger.info("all_orders_canceled")
            except Exception as e:
                logger.error("cancel_orders_error", error=str(e))
            if self.position_tracker.position_count() > 0:
                for pos in self.position_tracker.get_all_open_positions():
                    try:
                        await self.exchange.create_order(
                            symbol=pos.symbol,
                            side=OrderSide.SELL if pos.side == OrderSide.BUY else OrderSide.BUY,
                            order_type=OrderType.MARKET,
                            quantity=pos.quantity,
                        )
                        logger.info("position_closed_on_shutdown", symbol=pos.symbol)
                    except Exception as e:
                        logger.error("close_position_error", symbol=pos.symbol, error=str(e))
        else:
            if self.position_tracker.position_count() > 0:
                logger.info(
                    "paper_positions_remaining",
                    count=self.position_tracker.position_count(),
                )

        await self.redis.disconnect()
        if self.exchange:
            await self.exchange.close()
        if self._realtime:
            await self._realtime.stop()
        logger.info("trader_bot_stopped")

    async def _handle_signal(self, data: dict) -> None:
        try:
            signal = Signal(**data)
        except Exception as e:
            logger.error("invalid_signal", error=str(e), data=data)
            return

        self._last_signal_time = datetime.now(timezone.utc)

        if self._standby:
            self._standby = False
            logger.info("trader_now_active")

        symbol = signal.symbol
        logger.info(
            "signal_received",
            symbol=symbol,
            action=signal.action.value,
            confidence=round(signal.confidence, 3),
        )

        if signal.action == SignalAction.HOLD:
            return

        can_trade, reason = self.risk_manager.can_trade(symbol)
        if not can_trade:
            logger.warning("trade_blocked", symbol=symbol, reason=reason)
            return

        has_position = self.position_tracker.has_position(symbol)
        if has_position and signal.action == SignalAction.BUY:
            logger.info("already_in_position", symbol=symbol)
            return
        if has_position and signal.action == SignalAction.SELL:
            await self._close_position(symbol, signal.price, "signal")
            return
        if not has_position and signal.action == SignalAction.BUY:
            await self._open_position(symbol, signal.price)
            return

    async def _open_position(self, symbol: str, price: float) -> None:
        current_balance = self.paper_engine.balance if self.mode == BotMode.PAPER else 10000.0
        self.risk_manager.update_balance(current_balance)

        quantity = self.risk_manager.calculate_position_size(current_balance, price)
        if quantity <= 0:
            logger.warning("invalid_quantity", symbol=symbol)
            return

        trader_cfg = self.settings.get("trader", {})
        sl_pct = trader_cfg.get("default_sl_pct", 2.0)
        tp_pct = trader_cfg.get("default_tp_pct", 4.0)
        stop_loss = price * (1 - sl_pct / 100)
        take_profit = price * (1 + tp_pct / 100)

        if self.mode == BotMode.PAPER:
            order = await self.paper_engine.create_order(
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=quantity,
                price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
            )
            fill_price = order.average_fill_price
        else:
            result = await self.exchange.create_order(
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=quantity,
                price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
            )
            fill_price = float(result.get("price", price))

        pos = self.position_tracker.open_position(
            symbol=symbol,
            side=OrderSide.BUY,
            entry_price=fill_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )
        self.risk_manager.record_trade(symbol)

        try:
            await save_position(pos, self.mode.value)
            await save_trade(
                symbol=symbol,
                side="buy",
                price=fill_price,
                quantity=quantity,
                fee=0.001 * fill_price * quantity,
                mode=self.mode.value,
            )
        except Exception as e:
            logger.error("db_save_trade_error", error=str(e))

        await self.notifier.send_trade_notification(
            symbol=symbol,
            action="buy",
            price=fill_price,
            quantity=quantity,
        )

    async def _close_position(self, symbol: str, price: float, reason: str) -> None:
        pos = self.position_tracker.get_open_position(symbol)
        if not pos:
            return

        if self.mode == BotMode.PAPER:
            await self.paper_engine.create_order(
                symbol=symbol,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                quantity=pos.quantity,
                price=price,
            )
            exit_price = price
        else:
            result = await self.exchange.create_order(
                symbol=symbol,
                side=OrderSide.SELL,
                order_type=OrderType.MARKET,
                quantity=pos.quantity,
            )
            exit_price = float(result.get("price", price))

        closed = self.position_tracker.close_position(symbol, exit_price, reason)
        if closed:
            self.risk_manager.update_balance(
                self.paper_engine.balance if self.mode == BotMode.PAPER else 10000.0
            )

            try:
                await save_trade(
                    symbol=symbol,
                    side="sell",
                    price=exit_price,
                    quantity=pos.quantity,
                    fee=0.001 * exit_price * pos.quantity,
                    pnl=closed.realized_pnl,
                    mode=self.mode.value,
                )
            except Exception as e:
                logger.error("db_save_trade_error", error=str(e))

            await self.notifier.send_trade_notification(
                symbol=symbol,
                action="sell",
                price=exit_price,
                quantity=pos.quantity,
                pnl=closed.realized_pnl,
            )

    async def _handle_heartbeat(self, data: dict) -> None:
        self._last_heartbeat = datetime.now(timezone.utc)
        if self._standby:
            logger.info("analyst_heartbeat_received_entering_active")

    async def _monitor_loop(self) -> None:
        async def heartbeat_callback(data: dict) -> None:
            self._last_heartbeat = datetime.now(timezone.utc)
            if self._standby:
                logger.info("analyst_heartbeat_received_entering_active")
                self._standby = False

        asyncio.create_task(
            self.redis.subscribe(self.heartbeat_channel, heartbeat_callback)
        )

        while self._running:
            now = datetime.now(timezone.utc)
            if self._last_heartbeat and (now - self._last_heartbeat).total_seconds() > self.heartbeat_timeout:
                logger.warning("analyst_heartbeat_lost")
                self._standby = True
            if self._last_signal_time and (now - self._last_signal_time).total_seconds() > self.stale_signal_timeout:
                logger.warning("signals_stale_entering_standby")
                self._standby = True
            await asyncio.sleep(15)
