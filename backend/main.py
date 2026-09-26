from fastapi import FastAPI
from backend.api.routes import router as core_router
from backend.api.analysis import router as analysis_router
from backend.api.market import router as market_router

app = FastAPI(title="Stock Intelligence API", version="0.3.0")
app.include_router(core_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(market_router, prefix="/api")

@app.get("/health")
def health():
    return {"status":"ok","service":"stock-intelligence","version":"0.3.0"}
