import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.schemas import (
    MarketIndices,
    Indicator,
    LatestMacro,
    MacroStat,
    PCEStat,
    FedRate,
    VIXClose,
)


@pytest.mark.asyncio
async def test_api_market_indices_ok(mocker):
    mock_ticker = mocker.patch("yfinance.Ticker")
    mock_ticker.return_value.fast_info = {"last_price": 1, "last_volume": 2}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/market_indices")
    assert resp.status_code == 200
    data = resp.json()
    assert data["dxy_proxy_uup"]["symbol"] == "UUP"


@pytest.mark.asyncio
async def test_api_market_indices_error(mocker):
    mocker.patch("yfinance.Ticker", side_effect=Exception)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/market_indices")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_latest_macro_ok(mocker):
    payload = LatestMacro(latest_macro=MacroStat(name="CPI", value=1.0, unit="i", date="2024-06", source="BLS"))
    mocker.patch("app.crud.fetch_latest_macro", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/latest_macro")
    assert resp.status_code == 200
    assert resp.json()["latest_macro"]["name"] == "CPI"


@pytest.mark.asyncio
async def test_api_latest_macro_error(mocker):
    mocker.patch("app.crud.fetch_latest_macro", side_effect=RuntimeError)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/latest_macro")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_pce_ok(mocker):
    payload = PCEStat(name="PCE", value=0.1, unit="%", date="2024-06", source="BEA")
    mocker.patch("app.crud.fetch_pce", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/pce")
    assert resp.status_code == 200
    assert resp.json()["source"] == "BEA"


@pytest.mark.asyncio
async def test_api_pce_error(mocker):
    mocker.patch("app.crud.fetch_pce", side_effect=RuntimeError)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/pce")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_fed_rate_ok(mocker):
    payload = FedRate(value=5.0, date="2024-06-13")
    mocker.patch("app.crud.fetch_fed_rate", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/fed_rate")
    assert resp.status_code == 200
    assert resp.json()["source"] == "FRED"


@pytest.mark.asyncio
async def test_api_fed_rate_error(mocker):
    mocker.patch("app.crud.fetch_fed_rate", side_effect=RuntimeError)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/fed_rate")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_vix_ok(mocker):
    payload = VIXClose(value=15.5, date="2024-06-14")
    mocker.patch("app.crud.fetch_vix", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/vix")
    assert resp.status_code == 200
    assert resp.json()["source"] == "FRED"


@pytest.mark.asyncio
async def test_api_vix_error(mocker):
    mocker.patch("app.crud.fetch_vix", side_effect=RuntimeError)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/vix")
    assert resp.status_code == 503
