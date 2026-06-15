PLAN_LIMITS = {
    "basic": {
        "max_bots": 1,
        "max_pairs": 3,
        "max_position_usdt": 500,
        "spot_only": True,
    },
    "pro": {
        "max_bots": 3,
        "max_pairs": 10,
        "max_position_usdt": 5000,
        "spot_only": False,
    },
    "enterprise": {
        "max_bots": 999,
        "max_pairs": 999,
        "max_position_usdt": 999999,
        "spot_only": False,
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
