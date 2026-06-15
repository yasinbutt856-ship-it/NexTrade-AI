from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from db.models import UserRecord
from shared.redis_client import create_redis_client


class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.rpm = requests_per_minute

    async def __call__(self, user: UserRecord = None) -> None:
        if not user:
            return
        try:
            rc = create_redis_client()
            await rc.connect()
            key = f"ratelimit:user:{user.id}"
            now = int(datetime.now(timezone.utc).timestamp())
            window = now // 60
            window_key = f"{key}:{window}"
            count = await rc.get(window_key)
            if count and int(count) >= self.rpm:
                await rc.disconnect()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Try again in a minute.",
                )
            await rc.set(window_key, str(int(count or 0) + 1), ttl=120)
            await rc.disconnect()
        except HTTPException:
            raise
        except Exception:
            pass
