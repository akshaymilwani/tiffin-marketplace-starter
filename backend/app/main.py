import time
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api.router import api_router
from app.core.config import settings
from app.db.init_db import init_db

app = FastAPI(title=settings.APP_NAME)
_rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)

if settings.ALLOWED_HOSTS and "*" not in settings.ALLOWED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    protected_write = request.method in {"POST", "PUT", "PATCH", "DELETE"}
    auth_path = request.url.path.startswith("/api/v1/auth")
    if protected_write or auth_path:
        now = time.monotonic()
        client_host = request.client.host if request.client else "unknown"
        key = f"{client_host}:{request.url.path}"
        bucket = _rate_limit_buckets[key]
        while bucket and now - bucket[0] > settings.RATE_LIMIT_WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= settings.RATE_LIMIT_MAX_REQUESTS:
            return JSONResponse({"detail": "Too many requests"}, status_code=429)
        bucket.append(now)
    return await call_next(request)


@app.on_event("startup")
def on_startup() -> None:
    for attempt in range(10):
        try:
            init_db()
            return
        except OperationalError:
            if attempt == 9:
                raise
            time.sleep(2)


@app.get("/")
def root() -> dict:
    return {"message": "Tiffin Marketplace API is running"}

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")
