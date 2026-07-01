import asyncio
import json
import signal
from datetime import datetime, timezone

from analyst.data_fetcher import DataFetcher
from analyst.indicator_calculator import IndicatorCalculator
from guardian.crash_detector import CrashDetector
from shared.config_loader import ConfigLoader
from shared.logger import get_logger
from shared.redis_client import RedisClient

logger = get_logger(__name__)


class GuardianBot:
    def __init__(
        self,
        config_loader: ConfigLoader,
        redis_client: RedisClient,
    ):
        self.config_loader = config_loader
        self.redis = redis_client
        self.settings = config_loader.load_settings()
        self._running = False

        guardian_cfg = self.settings.get("guardian", {})
        redis_cfg = self.settings.get("redis", {})

        self.enabled = guardian_cfg.get("enabled", True)
        self.monitor_interval = guardian_cfg.get("monitor_interval_seconds", 60)
        self.heartbeat_interval = guardian_cfg.get("heartbeat_interval_seconds", 30)

        self.status_channel = redis_cfg.get("status_channel", "alerts:market:status")
        self.heartbeat_channel = redis_cfg.get("heartbeat_channel", "heartbeat:guardian")
        self.bot_name = self.settings.get("bot", {}).get("name", "mexc-trading-bot")

        self.data_fetcher = DataFetcher()
        self.indicator_calculator = IndicatorCalculator(self.settings.get("analyst", {}))
        self.crash_detector = CrashDetector(self.settings)

        self._last_status: dict = {
            "level": "GREEN",
            "score": 0.0,
            "triggers": [],
            "recommendation": "normal",
        }

    async def start(self) -> None:
        if not self.enabled:
            logger.info("guardian_disabled")
            return

        self._running = True
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
            except NotImplementedError:
                pass

        logger.info("connecting_to_redis")
        await self.redis.connect()
        logger.info("redis_connected")
        logger.info("guardian_bot_started")

        monitor_task = asyncio.create_task(self._monitor_loop())
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        await asyncio.gather(monitor_task, heartbeat_task)

    async def stop(self) -> None:
        self._running = False
        await self.redis.disconnect()
        await self.data_fetcher.close()
        logger.info("guardian_bot_stopped")

    async def _heartbeat_loop(self) -> None:
        while self._running:
            try:
                hb = {
                    "bot": self.bot_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "alive",
                    "level": self._last_status.get("level", "GREEN"),
                    "score": self._last_status.get("score", 0),
                }
                try:
                    await self.redis.lpush("heartbeat:guardian", json.dumps(hb))
                    await self.redis.ltrim("heartbeat:guardian", 0, 9)
                except Exception:
                    pass
            except Exception as e:
                logger.error("guardian_heartbeat_error", error=str(e))
            await asyncio.sleep(self.heartbeat_interval)

    async def _monitor_loop(self) -> None:
        while self._running:
            try:
                await self._analyze_and_publish()
            except Exception as e:
                logger.error("guardian_monitor_error", error=str(e))
            await asyncio.sleep(self.monitor_interval)

    async def _analyze_and_publish(self) -> None:
        status = await self.crash_detector.analyze(self.data_fetcher, self.indicator_calculator)

        self._last_status = status

        await self.redis.publish(self.status_channel, status)
        try:
            await self.redis.set("alerts:market:latest", json.dumps(status), ttl=3600)
            await self.redis.lpush("alerts:market:history", json.dumps(status))
            await self.redis.ltrim("alerts:market:history", 0, 99)
        except Exception as e:
            logger.error("redis_cache_guardian_error", error=str(e))

        logger.info(
            "market_status_published",
            level=status["level"],
            score=status["score"],
            triggers=status["triggers"],
        )

    def get_last_status(self) -> dict:
        return dict(self._last_status)
