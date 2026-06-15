from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from db.database import init_db, close_db
from web.routers import router
from web.auth_router import router as auth_router, seed_admin
from web.user_router import router as user_router
from web.auth import decode_token


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/api/") and path not in ("/api/status", "/api/logs", "/health"):
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                token = auth[7:]
                try:
                    payload = decode_token(token)
                    user_id = payload.get("user_id")
                    if user_id:
                        from shared.redis_client import create_redis_client
                        from datetime import datetime, timezone
                        rc = create_redis_client()
                        await rc.connect()
                        key = f"ratelimit:user:{user_id}"
                        now = int(datetime.now(timezone.utc).timestamp())
                        window = now // 60
                        window_key = f"{key}:{window}"
                        count = await rc.get(window_key)
                        if count and int(count) >= 60:
                            await rc.disconnect()
                            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
                        await rc.set(window_key, str(int(count or 0) + 1), ttl=120)
                        await rc.disconnect()
                except Exception:
                    pass
        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_admin()
    yield
    await close_db()


app = FastAPI(title="MEXC Trading Bot Dashboard", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://mexc-trading-bot.netlify.app",
        "https://mexc-trading-bot-production-c215.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
