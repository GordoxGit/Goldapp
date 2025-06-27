from fastapi import FastAPI, HTTPException

from .crud import (
    fetch_market_indices,
    fetch_latest_macro,
    fetch_pce,
    fetch_fed_rate,
    fetch_vix,
)
from .schemas import MarketIndices, LatestMacro, PCEStat, FedRate, VIXClose

app = FastAPI(title="Goldapp API")


# Returns UUP price and aggregated US equity volume.
# Any error leads to a 503 response for the API client.
@app.get("/api/v1/market_indices", response_model=MarketIndices)
def get_market_indices():
    try:
        data = fetch_market_indices()
    except Exception:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    if data is None:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    return data


@app.get("/api/v1/latest_macro", response_model=LatestMacro)
def get_latest_macro():
    try:
        data = fetch_latest_macro()
    except Exception:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    if data is None:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    return data


@app.get("/api/v1/pce", response_model=PCEStat)
def get_pce():
    try:
        data = fetch_pce()
    except Exception:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    if data is None:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    return data


@app.get("/api/v1/fed_rate", response_model=FedRate)
def get_fed_rate():
    try:
        data = fetch_fed_rate()
    except Exception:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    if data is None:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    return data


@app.get("/api/v1/vix", response_model=VIXClose)
def get_vix():
    try:
        data = fetch_vix()
    except Exception:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    if data is None:
        raise HTTPException(status_code=503, detail="Service Unavailable")
    return data
