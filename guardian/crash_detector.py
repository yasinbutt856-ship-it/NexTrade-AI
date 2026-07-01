import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional
import numpy as np
import pandas as pd

from shared.logger import get_logger

logger = get_logger(__name__)

MARKET_LEVELS = {
    "GREEN": {"score_range": (0, 25), "label": "Normal", "action": "normal"},
    "YELLOW": {"score_range": (25, 50), "label": "Caution", "action": "reduce_size"},
    "ORANGE": {"score_range": (50, 75), "label": "Warning", "action": "close_risky"},
    "RED": {"score_range": (75, 100), "label": "Danger", "action": "close_all"},
}


class CrashDetector:
    def __init__(self, config: dict):
        self.config = config.get("guardian", {})
        self.volatility_multiplier = self.config.get("volatility_multiplier", 2.5)
        self.flash_dip_threshold = self.config.get("flash_dip_threshold_pct", 3.0)
        self.volume_anomaly_multiplier = self.config.get("volume_anomaly_multiplier", 5.0)
        self.rsi_oversold = self.config.get("rsi_oversold", 30)
        self.rsi_overbought = self.config.get("rsi_overbought", 70)
        self.rsi_extreme_pct = self.config.get("rsi_extreme_pct", 40.0)
        self.correlation_deviation = self.config.get("correlation_deviation", 2.0)
        self.tracked_pairs = self.config.get("tracked_pairs", [
            "BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT",
            "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT",
        ])

        self._history: dict[str, list[dict]] = {}
        self._btc_eth_returns: list[float] = []
        self._last_level: Optional[str] = None

    async def analyze(self, data_fetcher, indicator_calculator) -> dict:
        triggers = []
        score = 0.0
        details = {}

        try:
            vol_score, vol_detail = await self._check_volatility(data_fetcher, indicator_calculator)
            score += vol_score
            if vol_detail.get("triggered"):
                triggers.append("volatility_spike")
            details["volatility"] = vol_detail
        except Exception as e:
            logger.warning("crash_detector_volatility_error", error=str(e))

        try:
            flash_score, flash_detail = await self._check_flash_dip(data_fetcher)
            score += flash_score
            if flash_detail.get("triggered"):
                triggers.append("flash_dip")
            details["flash_dip"] = flash_detail
        except Exception as e:
            logger.warning("crash_detector_flash_error", error=str(e))

        try:
            vol_score2, vol_detail2 = await self._check_volume_anomaly(data_fetcher)
            score += vol_score2
            if vol_detail2.get("triggered"):
                triggers.append("volume_anomaly")
            details["volume"] = vol_detail2
        except Exception as e:
            logger.warning("crash_detector_volume_error", error=str(e))

        try:
            rsi_score, rsi_detail = await self._check_rsi_extreme(data_fetcher, indicator_calculator)
            score += rsi_score
            if rsi_detail.get("triggered"):
                triggers.append("rsi_extreme")
            details["rsi"] = rsi_detail
        except Exception as e:
            logger.warning("crash_detector_rsi_error", error=str(e))

        try:
            corr_score, corr_detail = await self._check_correlation(data_fetcher)
            score += corr_score
            if corr_detail.get("triggered"):
                triggers.append("correlation_breakdown")
            details["correlation"] = corr_detail
        except Exception as e:
            logger.warning("crash_detector_correlation_error", error=str(e))

        final_score = min(score, 100.0)
        level = self._score_to_level(final_score)

        result = {
            "level": level,
            "score": round(final_score, 1),
            "triggers": triggers,
            "details": details,
            "recommendation": MARKET_LEVELS[level]["action"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._last_level = level
        return result

    def _score_to_level(self, score: float) -> str:
        for level, info in MARKET_LEVELS.items():
            lo, hi = info["score_range"]
            if lo <= score < hi:
                return level
        return "RED"

    async def _check_volatility(self, data_fetcher, indicator_calculator) -> tuple[float, dict]:
        triggered = False
        max_multiplier = 0.0
        pairs_above_threshold = 0
        total_checked = 0

        for symbol in self.tracked_pairs:
            df = await data_fetcher.fetch_ohlcv(symbol, "15m", limit=200)
            if df is None or df.empty or len(df) < 50:
                continue
            total_checked += 1
            df = indicator_calculator.calculate_all(df)
            if "atr" not in df.columns:
                continue

            atr_values = df["atr"].dropna().values
            if len(atr_values) < 30:
                continue

            recent_atr = atr_values[-5:].mean()
            historical_atr = atr_values[:-5].mean()
            if historical_atr <= 0:
                continue

            multiplier = recent_atr / historical_atr
            max_multiplier = max(max_multiplier, multiplier)
            if multiplier >= self.volatility_multiplier:
                pairs_above_threshold += 1

        trigger_pct = (pairs_above_threshold / total_checked * 100) if total_checked > 0 else 0
        triggered = pairs_above_threshold >= max(1, int(total_checked * 0.2))
        score = min(trigger_pct * 0.8, 30.0) if triggered else 0

        return score, {
            "triggered": triggered,
            "pairs_above_threshold": pairs_above_threshold,
            "total_checked": total_checked,
            "max_multiplier": round(max_multiplier, 2),
            "score_contribution": round(score, 1),
        }

    async def _check_flash_dip(self, data_fetcher) -> tuple[float, dict]:
        triggered = False
        pairs_dipping = 0
        max_drop_pct = 0.0
        total_checked = 0

        for symbol in self.tracked_pairs:
            df = await data_fetcher.fetch_ohlcv(symbol, "5m", limit=6)
            if df is None or df.empty or len(df) < 6:
                continue
            total_checked += 1
            closes = df["close"].values[-6:]
            drop_pct = ((closes[0] - closes[-1]) / closes[0]) * 100
            max_drop_pct = max(max_drop_pct, drop_pct)
            if drop_pct >= self.flash_dip_threshold:
                pairs_dipping += 1

        trigger_pct = (pairs_dipping / total_checked * 100) if total_checked > 0 else 0
        triggered = pairs_dipping >= max(1, int(total_checked * 0.15))
        score = min(trigger_pct * 0.6, 25.0) if triggered else 0

        return score, {
            "triggered": triggered,
            "pairs_dipping": pairs_dipping,
            "total_checked": total_checked,
            "max_drop_pct": round(max_drop_pct, 2),
            "score_contribution": round(score, 1),
        }

    async def _check_volume_anomaly(self, data_fetcher) -> tuple[float, dict]:
        triggered = False
        pairs_high_volume = 0
        max_volume_mult = 0.0
        total_checked = 0

        for symbol in self.tracked_pairs:
            df = await data_fetcher.fetch_ohlcv(symbol, "15m", limit=200)
            if df is None or df.empty or len(df) < 100:
                continue
            total_checked += 1
            volumes = df["volume"].values
            recent_vol = volumes[-6:].mean()
            historical_vol = volumes[:-6].mean()
            if historical_vol <= 0:
                continue
            multiplier = recent_vol / historical_vol
            max_volume_mult = max(max_volume_mult, multiplier)
            if multiplier >= self.volume_anomaly_multiplier:
                pairs_high_volume += 1

        trigger_pct = (pairs_high_volume / total_checked * 100) if total_checked > 0 else 0
        triggered = pairs_high_volume >= max(1, int(total_checked * 0.2))
        score = min(trigger_pct * 0.5, 20.0) if triggered else 0

        return score, {
            "triggered": triggered,
            "pairs_high_volume": pairs_high_volume,
            "total_checked": total_checked,
            "max_volume_multiplier": round(max_volume_mult, 1),
            "score_contribution": round(score, 1),
        }

    async def _check_rsi_extreme(self, data_fetcher, indicator_calculator) -> tuple[float, dict]:
        triggered = False
        extreme_pairs = 0
        total_checked = 0
        avg_rsi = 0.0

        for symbol in self.tracked_pairs:
            df = await data_fetcher.fetch_ohlcv(symbol, "1h", limit=100)
            if df is None or df.empty or len(df) < 30:
                continue
            total_checked += 1
            df = indicator_calculator.calculate_all(df)
            if "rsi" not in df.columns:
                continue
            rsi_val = df["rsi"].dropna().iloc[-1]
            avg_rsi += rsi_val
            if rsi_val <= self.rsi_oversold or rsi_val >= self.rsi_overbought:
                extreme_pairs += 1

        extreme_pct = (extreme_pairs / total_checked * 100) if total_checked > 0 else 0
        triggered = extreme_pct >= self.rsi_extreme_pct
        score = min(extreme_pct * 0.5, 15.0) if triggered else 0

        return score, {
            "triggered": triggered,
            "extreme_pairs": extreme_pairs,
            "total_checked": total_checked,
            "extreme_pct": round(extreme_pct, 1),
            "average_rsi": round(avg_rsi / total_checked, 1) if total_checked > 0 else 0,
            "score_contribution": round(score, 1),
        }

    async def _check_correlation(self, data_fetcher) -> tuple[float, dict]:
        triggered = False
        btc_returns = None
        eth_returns = None

        btc_df = await data_fetcher.fetch_ohlcv("BTC/USDT", "1h", limit=100)
        eth_df = await data_fetcher.fetch_ohlcv("ETH/USDT", "1h", limit=100)
        if btc_df is not None and not btc_df.empty and eth_df is not None and not eth_df.empty:
            btc_close = btc_df["close"].pct_change().dropna().values[-50:]
            eth_close = eth_df["close"].pct_change().dropna().values[-50:]
            if len(btc_close) > 10 and len(eth_close) == len(btc_close):
                corr = np.corrcoef(btc_close, eth_close)[0, 1]
                self._btc_eth_returns.append(corr)
                if len(self._btc_eth_returns) > 20:
                    self._btc_eth_returns = self._btc_eth_returns[-20:]

                if len(self._btc_eth_returns) >= 10:
                    rolling_mean = np.mean(self._btc_eth_returns[:-1])
                    rolling_std = np.std(self._btc_eth_returns[:-1])
                    if rolling_std > 0 and abs(corr - rolling_mean) > self.correlation_deviation * rolling_std:
                        triggered = True

        score = 10.0 if triggered else 0.0
        return score, {
            "triggered": triggered,
            "current_correlation": round(float(corr), 3) if btc_returns is not None else None,
            "score_contribution": round(score, 1),
        }

    def get_current_level(self) -> Optional[str]:
        return self._last_level
