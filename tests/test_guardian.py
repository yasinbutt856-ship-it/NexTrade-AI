import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timezone

from guardian.crash_detector import CrashDetector, MARKET_LEVELS


class TestCrashDetector:
    @pytest.fixture
    def config(self) -> dict:
        return {
            "guardian": {
                "enabled": True,
                "volatility_multiplier": 2.5,
                "flash_dip_threshold_pct": 3.0,
                "volume_anomaly_multiplier": 5.0,
                "rsi_oversold": 30,
                "rsi_overbought": 70,
                "rsi_extreme_pct": 40.0,
                "correlation_deviation": 2.0,
                "tracked_pairs": ["BTC/USDT", "ETH/USDT"],
            }
        }

    @pytest.fixture
    def detector(self, config) -> CrashDetector:
        return CrashDetector(config)

    def test_score_to_level_green(self, detector):
        assert detector._score_to_level(10) == "GREEN"

    def test_score_to_level_yellow(self, detector):
        assert detector._score_to_level(30) == "YELLOW"

    def test_score_to_level_orange(self, detector):
        assert detector._score_to_level(60) == "ORANGE"

    def test_score_to_level_red(self, detector):
        assert detector._score_to_level(80) == "RED"

    def test_score_to_level_boundary_green_yellow(self, detector):
        assert detector._score_to_level(24.9) == "GREEN"
        assert detector._score_to_level(25) == "YELLOW"

    def test_score_to_level_boundary_yellow_orange(self, detector):
        assert detector._score_to_level(49.9) == "YELLOW"
        assert detector._score_to_level(50) == "ORANGE"

    def test_score_to_level_boundary_orange_red(self, detector):
        assert detector._score_to_level(74.9) == "ORANGE"
        assert detector._score_to_level(75) == "RED"

    def test_score_to_level_max(self, detector):
        assert detector._score_to_level(100) == "RED"
        assert detector._score_to_level(200) == "RED"

    def test_market_levels_structure(self):
        assert "GREEN" in MARKET_LEVELS
        assert "YELLOW" in MARKET_LEVELS
        assert "ORANGE" in MARKET_LEVELS
        assert "RED" in MARKET_LEVELS
        for level, info in MARKET_LEVELS.items():
            assert "score_range" in info
            assert "label" in info
            assert "action" in info
            assert len(info["score_range"]) == 2
            assert info["score_range"][0] <= info["score_range"][1]

    def test_get_current_level_returns_none_initially(self, detector):
        assert detector.get_current_level() is None

    def test_analyze_returns_expected_structure(self, detector):
        from unittest.mock import AsyncMock
        data_fetcher = AsyncMock()
        data_fetcher.fetch_ohlcv = AsyncMock(return_value=None)
        indicator_calc = AsyncMock()
        indicator_calc.calculate_all = AsyncMock(return_value=pd.DataFrame())

        import asyncio
        result = asyncio.run(detector.analyze(data_fetcher, indicator_calc))

        assert "level" in result
        assert "score" in result
        assert "triggers" in result
        assert "details" in result
        assert "recommendation" in result
        assert "timestamp" in result
        assert result["level"] in ("GREEN", "YELLOW", "ORANGE", "RED")


class TestMarketLevels:
    def test_all_levels_have_actions(self):
        actions = {info["action"] for info in MARKET_LEVELS.values()}
        assert "normal" in actions
        assert "reduce_size" in actions
        assert "close_risky" in actions
        assert "close_all" in actions

    def test_size_multipliers_decrease(self):
        from trader.risk_manager import MARKET_LEVELS as RM_LEVELS
        assert RM_LEVELS["GREEN"]["size_multiplier"] == 1.0
        assert RM_LEVELS["YELLOW"]["size_multiplier"] == 0.5
        assert RM_LEVELS["ORANGE"]["size_multiplier"] == 0.0
        assert RM_LEVELS["RED"]["size_multiplier"] == 0.0
        assert RM_LEVELS["GREEN"]["can_open"] is True
        assert RM_LEVELS["YELLOW"]["can_open"] is True
        assert RM_LEVELS["ORANGE"]["can_open"] is False
        assert RM_LEVELS["RED"]["can_open"] is False


class TestCrashDetectionLogic:
    @pytest.fixture
    def sample_volatile_df(self) -> pd.DataFrame:
        np.random.seed(42)
        dates = pd.date_range("2026-01-01", periods=200, freq="15min")
        close = np.random.randn(200).cumsum() + 100
        close[-10:] = close[-10:] + np.random.randn(10) * 5
        return pd.DataFrame({
            "open": close + np.random.randn(200) * 0.1,
            "high": close + np.abs(np.random.randn(200)) * 1.0,
            "low": close - np.abs(np.random.randn(200)) * 1.0,
            "close": close,
            "volume": np.random.rand(200) * 1000 + 500,
            "timestamp": dates,
        })

    def test_volatility_detection_high_vol(self, sample_volatile_df):
        from analyst.indicator_calculator import IndicatorCalculator
        config = {"guardian": {"volatility_multiplier": 1.5}}
        detector = CrashDetector(config)
        calc = IndicatorCalculator({"indicator_periods": {}})
        df = calc.calculate_all(sample_volatile_df)
        assert "rsi" in df.columns
        assert "bb_upper" in df.columns
        assert "volume_ma" in df.columns

    def test_flash_dip_threshold_config(self):
        config = {"guardian": {"flash_dip_threshold_pct": 2.0}}
        detector = CrashDetector(config)
        assert detector.flash_dip_threshold == 2.0
        assert detector.volatility_multiplier == 2.5

    def test_volume_anomaly_detection(self):
        config = {"guardian": {"volume_anomaly_multiplier": 3.0}}
        detector = CrashDetector(config)
        assert detector.volume_anomaly_multiplier == 3.0
        assert detector._score_to_level(0) == "GREEN"
