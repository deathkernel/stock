from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(
    title="Stock Intelligence API",
    version="0.1.0",
    description="Market analysis, forecasting, risk and explainability API.",
)

app.include_router(router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok", "service": "stock-intelligence"}
