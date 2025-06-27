from fastapi import FastAPI, HTTPException

from .crud import fetch_market_indices
from .schemas import MarketIndices

app = FastAPI(title="Goldapp API")


@app.get("/api/v1/market_indices", response_model=MarketIndices)
def get_market_indices():
    try:
        return fetch_market_indices()
    except Exception:
        raise HTTPException(status_code=503, detail="Data source unavailable")
