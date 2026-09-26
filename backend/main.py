from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from backend.api.routes import router as core_router
from backend.api.analysis import router as analysis_router
from backend.api.market import router as market_router
from backend.api.ml import router as ml_router
from backend.api.research import router as research_router
from backend.api.portfolio import router as portfolio_router
from backend.cache import research_cache
from backend.config import settings
from backend.observability import metrics, observe_request
from backend.storage import check_db, init_db


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


init_db()
app = FastAPI(title="Stock Intelligence API", version="0.7.0")
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=observe_request)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Request-ID"],
)
app.include_router(core_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(market_router, prefix="/api")
app.include_router(ml_router, prefix="/api")
app.include_router(research_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok", "service": "stock-intelligence", "version": "0.7.0"}


@app.get("/ready")
def ready():
    try:
        check_db()
    except Exception:
        return {"status": "not_ready", "service": "stock-intelligence", "version": "0.7.0"}
    return {"status": "ready", "service": "stock-intelligence", "version": "0.7.0"}


@app.get("/metrics")
def app_metrics():
    return {
        "service": "stock-intelligence",
        "version": "0.7.0",
        "requests": metrics(),
        "research_cache": research_cache.stats(),
    }
