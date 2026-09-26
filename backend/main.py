from fastapi import FastAPI
from backend.api.routes import router as core_router
from backend.api.analysis import router as analysis_router
from backend.api.market import router as market_router
from backend.api.ml import router as ml_router
from backend.api.research import router as research_router
from backend.storage import init_db

init_db()
app=FastAPI(title="Stock Intelligence API",version="0.5.0")
app.include_router(core_router,prefix="/api")
app.include_router(analysis_router,prefix="/api")
app.include_router(market_router,prefix="/api")
app.include_router(ml_router,prefix="/api")
app.include_router(research_router,prefix="/api")

@app.get("/health")
def health():
    return {"status":"ok","service":"stock-intelligence","version":"0.5.0"}
