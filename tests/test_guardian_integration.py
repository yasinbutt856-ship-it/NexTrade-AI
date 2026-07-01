import pytest
from unittest.mock import AsyncMock, patch

from trader.risk_manager import RiskManager, MARKET_LEVELS
from shared.models import OrderSide


class TestGuardianTraderIntegration:
    def test_risk_manager_initial_level_is_green(self):
        rm = RiskManager()
        assert rm.get_market_level() == "GREEN"
        assert rm.get_size_multiplier() == 1.0
        assert rm.can_open_new_positions() is True
        assert rm.get_market_recommendation() == "normal"

    def test_set_market_status_green(self):
        rm = RiskManager()
        rm.set_market_status("GREEN", "normal", [])
        assert rm.get_market_level() == "GREEN"
        assert rm.get_size_multiplier() == 1.0
        assert rm.can_open_new_positions() is True

    def test_set_market_status_yellow(self):
        rm = RiskManager()
        rm.set_market_status("YELLOW", "reduce_size", ["volatility_spike"])
        assert rm.get_market_level() == "YELLOW"
        assert rm.get_size_multiplier() == 0.5
        assert rm.can_open_new_positions() is True
        assert rm.get_crash_triggers() == ["volatility_spike"]

    def test_set_market_status_orange(self):
        rm = RiskManager()
        rm.set_market_status("ORANGE", "close_risky", ["flash_dip"])
        assert rm.get_market_level() == "ORANGE"
        assert rm.get_size_multiplier() == 0.0
        assert rm.can_open_new_positions() is False

    def test_set_market_status_red(self):
        rm = RiskManager()
        rm.set_market_status("RED", "close_all", ["crash_detected"])
        assert rm.get_market_level() == "RED"
        assert rm.get_size_multiplier() == 0.0
        assert rm.can_open_new_positions() is False

    def test_unknown_level_ignored(self):
        rm = RiskManager()
        rm.set_market_status("UNKNOWN", "normal", [])
        assert rm.get_market_level() == "GREEN"

    def test_position_size_reduced_in_yellow(self):
        rm = RiskManager(max_position_size_usdt=1000.0)
        assert rm.calculate_position_size(100000.0, 50000.0) == 0.02

        rm.set_market_status("YELLOW", "reduce_size", [])
        reduced = rm.calculate_position_size(100000.0, 50000.0)
        assert reduced == 0.01

    def test_trade_blocked_in_orange(self):
        rm = RiskManager()
        rm.set_market_status("ORANGE", "close_risky", [])
        can, reason = rm.can_trade("BTC/USDT")
        assert can is False
        assert "ORANGE" in reason

    def test_trade_blocked_in_red(self):
        rm = RiskManager()
        rm.set_market_status("RED", "close_all", [])
        can, reason = rm.can_trade("BTC/USDT")
        assert can is False
        assert "RED" in reason

    def test_trade_allowed_in_green(self):
        rm = RiskManager()
        rm.set_market_status("GREEN", "normal", [])
        can, reason = rm.can_trade("BTC/USDT")
        assert can is True

    def test_trade_allowed_in_yellow(self):
        rm = RiskManager()
        rm.set_market_status("YELLOW", "reduce_size", [])
        can, reason = rm.can_trade("BTC/USDT")
        assert can is True

    def test_market_status_resets_after_reenable(self):
        rm = RiskManager()
        rm.set_market_status("RED", "close_all", ["crash"])
        assert rm.can_open_new_positions() is False
        rm.set_market_status("GREEN", "normal", [])
        assert rm.can_open_new_positions() is True
        assert rm.get_size_multiplier() == 1.0

    def test_multiple_levels_trigger_updates(self):
        rm = RiskManager()
        levels = ["GREEN", "YELLOW", "ORANGE", "RED", "GREEN"]
        for level in levels:
            rm.set_market_status(level, "normal", [])
        assert rm.get_market_level() == "GREEN"

    def test_crash_triggers_stored_correctly(self):
        rm = RiskManager()
        triggers = ["volatility_spike", "flash_dip", "volume_anomaly"]
        rm.set_market_status("ORANGE", "close_risky", triggers)
        assert rm.get_crash_triggers() == triggers

    def test_market_recommendation_stored(self):
        rm = RiskManager()
        rm.set_market_status("RED", "close_all", [])
        assert rm.get_market_recommendation() == "close_all"


class TestAllLevelsCovered:
    def test_str_to_level_mapping(self):
        from guardian.crash_detector import MARKET_LEVELS as CD_LEVELS
        from trader.risk_manager import MARKET_LEVELS as RM_LEVELS

        for level in CD_LEVELS:
            assert level in RM_LEVELS, f"Missing level {level} in risk manager"

        for level in RM_LEVELS:
            assert level in CD_LEVELS, f"Missing level {level} in crash detector"
