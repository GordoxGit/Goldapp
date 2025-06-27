from fastapi.testclient import TestClient
import types

from app.main import app
import app.crud as crud


class DummyTicker:
    def __init__(self, symbol, calls):
        self.symbol = symbol
        self.calls = calls
        self.calls.append(symbol)

    @property
    def fast_info(self):
        return {"last_price": 1.0, "last_volume": 2.0}


class FailingTicker:
    def __init__(self, symbol):
        raise Exception("network error")


def test_market_indices_success(monkeypatch):
    calls = []
    monkeypatch.setattr(crud.yf, "Ticker", lambda symbol: DummyTicker(symbol, calls))
    crud.CACHE.clear()
    client = TestClient(app)
    resp = client.get("/api/v1/market_indices")
    assert resp.status_code == 200
    data = resp.json()
    assert data["dxy_proxy_uup"]["value"] == 1.0
    assert data["volume_aggregated"]["value"] == 4.0
    assert len(calls) == 3


def test_market_indices_failure(monkeypatch):
    monkeypatch.setattr(crud.yf, "Ticker", FailingTicker)
    crud.CACHE.clear()
    client = TestClient(app)
    resp = client.get("/api/v1/market_indices")
    assert resp.status_code == 503


def test_market_indices_cache(monkeypatch):
    calls = []
    monkeypatch.setattr(crud.yf, "Ticker", lambda symbol: DummyTicker(symbol, calls))
    crud.CACHE.clear()
    # first call
    crud.fetch_market_indices()
    # second call within TTL
    crud.fetch_market_indices()
    # Should have only one round of yfinance access for three tickers
    assert len(calls) == 3
