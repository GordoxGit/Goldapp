from fastapi import FastAPI, HTTPException

from .crud import fetch_market_indices, fetch_latest_macro
from .schemas import MarketIndices, LatestMacro

app = FastAPI(title="Goldapp API")


@app.get("/api/v1/market_indices", response_model=MarketIndices)
def get_market_indices():
    try:
        return fetch_market_indices()
    except Exception:
        raise HTTPException(status_code=503, detail="Data source unavailable")


@app.get("/api/v1/latest_macro", response_model=LatestMacro)
def get_latest_macro():
    try:
        return fetch_latest_macro()
    except Exception:
        raise HTTPException(status_code=503, detail="Data source unavailable")
