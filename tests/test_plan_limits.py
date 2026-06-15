import pytest
from shared.plan_limits import PLAN_LIMITS, get_plan_limits, enforce_plan_limit


class TestPlanLimits:
    def test_get_plan_limits_basic(self):
        limits = get_plan_limits("basic")
        assert limits["max_bots"] == 1
        assert limits["max_pairs"] == 3
        assert limits["max_position_usdt"] == 500
        assert limits["spot_only"] is True

    def test_get_plan_limits_pro(self):
        limits = get_plan_limits("pro")
        assert limits["max_bots"] == 3
        assert limits["max_pairs"] == 10
        assert limits["max_position_usdt"] == 5000
        assert limits["spot_only"] is False

    def test_get_plan_limits_enterprise(self):
        limits = get_plan_limits("enterprise")
        assert limits["max_bots"] == 999
        assert limits["max_pairs"] == 999
        assert limits["spot_only"] is False

    def test_get_plan_limits_unknown_falls_back_to_basic(self):
        limits = get_plan_limits("nonexistent")
        assert limits["max_bots"] == 1

    def test_enforce_plan_limit_within_bounds(self):
        ok, msg = enforce_plan_limit("basic", "max_position_usdt", 300)
        assert ok is True
        assert msg == ""

    def test_enforce_plan_limit_exceeds(self):
        ok, msg = enforce_plan_limit("basic", "max_position_usdt", 501)
        assert ok is False
        assert "max_position_usdt" in msg

    def test_enforce_plan_limit_exact_boundary(self):
        ok, msg = enforce_plan_limit("basic", "max_position_usdt", 500)
        assert ok is True

    def test_enforce_plan_limit_non_numeric(self):
        ok, msg = enforce_plan_limit("basic", "max_bots", 0)
        assert ok is True

    def test_plan_limits_structure(self):
        for plan, limits in PLAN_LIMITS.items():
            assert "max_bots" in limits
            assert "max_pairs" in limits
            assert "max_position_usdt" in limits
            assert "spot_only" in limits
