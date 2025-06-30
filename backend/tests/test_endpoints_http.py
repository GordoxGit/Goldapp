import pytest
from datetime import datetime

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
    payload = MarketIndices(
        dxy_proxy_uup=Indicator(
            symbol="UUP", value=1.0, unit="USD", last_updated_utc=datetime.utcnow()
        ),
        volume_aggregated=Indicator(
            symbol="US_VOLUME",
            value=2.0,
            unit="shares",
            last_updated_utc=datetime.utcnow(),
        ),
    )
    mocker.patch("app.main.fetch_market_indices", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/market_indices")
    assert resp.status_code == 200
    data = resp.json()
    assert data["dxy_proxy_uup"]["symbol"] == "UUP"


@pytest.mark.asyncio
async def test_api_market_indices_error(mocker):
    from app.crud import fetch_market_indices

    fetch_market_indices.cache_clear()
    mocker.patch("app.main.fetch_market_indices", side_effect=Exception)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/market_indices")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_market_indices_none(mocker):
    from app.crud import fetch_market_indices

    fetch_market_indices.cache_clear()
    mocker.patch("app.main.fetch_market_indices", return_value=None)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/market_indices")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_latest_macro_ok(mocker):
    payload = LatestMacro(latest_macro=MacroStat(name="CPI", value=1.0, unit="i", date="2024-06", source="BLS"))
    mocker.patch("app.main.fetch_latest_macro", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/latest_macro")
    assert resp.status_code == 200
    assert resp.json()["latest_macro"]["name"] == "CPI"


@pytest.mark.asyncio
async def test_api_latest_macro_error(mocker):
    mocker.patch("app.main.fetch_latest_macro", side_effect=RuntimeError)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/latest_macro")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_pce_ok(mocker):
    payload = PCEStat(name="PCE", value=0.1, unit="%", date="2024-06", source="BEA")
    mocker.patch("app.main.fetch_pce", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/pce")
    assert resp.status_code == 200
    assert resp.json()["source"] == "BEA"


@pytest.mark.asyncio
async def test_api_pce_error(mocker):
    mocker.patch("app.main.fetch_pce", side_effect=RuntimeError)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/pce")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_fed_rate_ok(mocker):
    payload = FedRate(value=5.0, date="2024-06-13")
    mocker.patch("app.main.fetch_fed_rate", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/fed_rate")
    assert resp.status_code == 200
    assert resp.json()["source"] == "FRED"


@pytest.mark.asyncio
async def test_api_fed_rate_error(mocker):
    mocker.patch("app.main.fetch_fed_rate", side_effect=RuntimeError)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/fed_rate")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_vix_ok(mocker):
    payload = VIXClose(value=15.5, date="2024-06-14")
    mocker.patch("app.main.fetch_vix", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/vix")
    assert resp.status_code == 200
    assert resp.json()["source"] == "FRED"


@pytest.mark.asyncio
async def test_api_vix_error(mocker):
    mocker.patch("app.main.fetch_vix", side_effect=RuntimeError)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/vix")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_api_fomc_next_ok(mocker):
    from app.schemas import FomcNext

    payload = FomcNext(date="2099-01-01", time="12:00", title="Meeting", url="u")
    mocker.patch("app.main.fetch_fomc_next", return_value=payload)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/fomc_next")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Meeting"


@pytest.mark.asyncio
async def test_api_fomc_next_error(mocker):
    mocker.patch("app.main.fetch_fomc_next", side_effect=RuntimeError)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/fomc_next")
    assert resp.status_code == 503
