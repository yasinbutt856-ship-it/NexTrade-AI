PLAN_LIMITS = {
    "basic": {
        "max_bots": 1,
        "max_pairs": 3,
        "max_position_usdt": 500,
        "spot_only": True,
        "free_trial_days": 14,
        "max_api_calls_per_day": 100,
        "max_bot_hours_per_month": 720,
        "max_trade_volume_per_month": 50000,
    },
    "pro": {
        "max_bots": 3,
        "max_pairs": 10,
        "max_position_usdt": 5000,
        "spot_only": False,
        "free_trial_days": 14,
        "max_api_calls_per_day": 1000,
        "max_bot_hours_per_month": 720,
        "max_trade_volume_per_month": 500000,
    },
    "enterprise": {
        "max_bots": 999,
        "max_pairs": 999,
        "max_position_usdt": 999999,
        "spot_only": False,
        "free_trial_days": 14,
        "max_api_calls_per_day": 10000,
        "max_bot_hours_per_month": 720,
        "max_trade_volume_per_month": 99999999,
    },
}


def get_plan_limits(plan: str) -> dict:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["basic"])


def enforce_plan_limit(plan: str, field: str, value) -> tuple[bool, str]:
    limits = get_plan_limits(plan)
    max_val = limits.get(field)
    if max_val is not None and isinstance(value, (int, float)) and value > max_val:
        return False, f"{field} limit for {plan} plan is {max_val}"
    return True, ""


from datetime import datetime, timezone


def is_trial_expired(user) -> bool:
    if user.trial_end is None:
        return False
    return datetime.now(timezone.utc) > user.trial_end.replace(tzinfo=timezone.utc)


def enforce_trial(user) -> bool:
    if is_trial_expired(user) and user.plan == "basic":
        return False
    return True


def enforce_usage_limit(plan: str, field: str, current_value: int | float) -> tuple[bool, str]:
    limits = get_plan_limits(plan)
    max_val = limits.get(field)
    if max_val is not None and current_value >= max_val:
        return False, f"{field} limit reached for {plan} plan (max: {max_val})"
    return True, ""


def get_usage_limits(plan: str) -> dict:
    limits = get_plan_limits(plan)
    return {
        "max_api_calls_per_day": limits.get("max_api_calls_per_day", 100),
        "max_bot_hours_per_month": limits.get("max_bot_hours_per_month", 720),
        "max_trade_volume_per_month": limits.get("max_trade_volume_per_month", 50000),
    }
