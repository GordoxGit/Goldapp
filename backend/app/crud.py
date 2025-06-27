from datetime import datetime
from cachetools import cached, TTLCache
import requests
import yfinance as yf

from .config import settings
from .schemas import MarketIndices, Indicator, MacroStat, LatestMacro, PCEStat

CACHE = TTLCache(maxsize=8, ttl=settings.ttl)
MACRO_CACHE = TTLCache(maxsize=2, ttl=86400)
PCE_CACHE = TTLCache(maxsize=1, ttl=86400)

BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
BLS_CPI_SERIES = "CUUR0000SA0"
BLS_NFP_SERIES = "CES0000000001"
BEA_BASE_URL = "https://apps.bea.gov/api/data/"


def _get_fast_info_value(info: dict, key_base: str):
    return info.get(key_base) or info.get(key_base.capitalize()) or info.get(key_base.replace('_', '').capitalize())


@cached(CACHE)
def fetch_market_indices() -> MarketIndices:
    """Fetch UUP last price and aggregated US volume from SPY and QQQ."""
    try:
        uup_info = yf.Ticker("UUP").fast_info
        spy_info = yf.Ticker("SPY").fast_info
        qqq_info = yf.Ticker("QQQ").fast_info

        price = _get_fast_info_value(uup_info, "last_price")
        vol_spy = _get_fast_info_value(spy_info, "last_volume")
        vol_qqq = _get_fast_info_value(qqq_info, "last_volume")

        if price is None or vol_spy is None or vol_qqq is None:
            raise RuntimeError("Missing data from yfinance")

        now = datetime.utcnow()
        return MarketIndices(
            dxy_proxy_uup=Indicator(
                symbol="UUP",
                value=float(price),
                unit="USD",
                last_updated_utc=now,
            ),
            volume_aggregated=Indicator(
                symbol="US_VOLUME",
                value=float(vol_spy) + float(vol_qqq),
                unit="shares",
                last_updated_utc=now,
            ),
        )
    except Exception as exc:
        # Clear cache entry on error
        CACHE.clear()
        raise RuntimeError("yfinance unavailable") from exc


def _fetch_bls_series(series_id: str, name: str, unit: str) -> MacroStat:
    params = {"latest": "true"}
    if settings.bls_api_key:
        params["registrationKey"] = settings.bls_api_key
    resp = requests.get(f"{BLS_BASE_URL}{series_id}", params=params, timeout=10)
    resp.raise_for_status()
    json_data = resp.json()
    item = json_data["Results"]["series"][0]["data"][0]
    year = item["year"]
    month = item["period"].lstrip("M")
    return MacroStat(
        name=name,
        value=float(item["value"]),
        unit=unit,
        date=f"{year}-{month}",
        source="BLS",
    )


@cached(MACRO_CACHE)
def fetch_latest_macro() -> LatestMacro:
    """Return the most recently published macro indicator between CPI and NFP."""
    try:
        cpi = _fetch_bls_series(BLS_CPI_SERIES, "CPI", "index")
        nfp = _fetch_bls_series(BLS_NFP_SERIES, "NFP", "k jobs")
        latest = cpi if cpi.date >= nfp.date else nfp
        return LatestMacro(latest_macro=latest)
    except Exception as exc:
        MACRO_CACHE.clear()
        raise RuntimeError("BLS unavailable") from exc


@cached(PCE_CACHE)
def fetch_pce() -> PCEStat:
    """Return the latest monthly PCE percent change from BEA."""
    if not settings.bea_api_key:
        raise RuntimeError("BEA API key missing")

    params = {
        "UserID": settings.bea_api_key,
        "method": "GetData",
        "datasetname": "NIPA",
        "TableName": "T20807",
        "Frequency": "M",
        "Year": "latest",
        "ResultFormat": "JSON",
    }

    try:
        resp = requests.get(BEA_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        json_data = resp.json()
        data = json_data["BEAAPI"]["Results"]["Data"]
        latest = max(data, key=lambda item: item["TimePeriod"])
        period = latest["TimePeriod"]
        if "M" in period:
            year, month = period.split("M")
        else:
            year, month = period.split("-")[:2]
        return PCEStat(
            name="PCE",
            value=float(latest["DataValue"]),
            unit="%",
            date=f"{year}-{month}",
            source="BEA",
        )
    except Exception as exc:
        PCE_CACHE.clear()
        raise RuntimeError("BEA unavailable") from exc
