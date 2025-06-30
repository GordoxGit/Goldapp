from datetime import datetime
from xml.etree import ElementTree
from cachetools import cached, TTLCache
import requests
import yfinance as yf

from .config import settings
from .schemas import (
    MarketIndices,
    Indicator,
    MacroStat,
    LatestMacro,
    PCEStat,
    FedRate,
    VIXClose,
    FomcNext,
)

CACHE = TTLCache(maxsize=8, ttl=settings.ttl)
MACRO_CACHE = TTLCache(maxsize=2, ttl=86400)
PCE_CACHE = TTLCache(maxsize=1, ttl=86400)
FRED_RATE_CACHE = TTLCache(maxsize=1, ttl=21600)
VIX_CACHE = TTLCache(maxsize=1, ttl=21600)
FOMC_NEXT_CACHE = TTLCache(maxsize=1, ttl=86400)

BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
BLS_CPI_SERIES = "CUUR0000SA0"
BLS_NFP_SERIES = "CES0000000001"
BEA_BASE_URL = "https://apps.bea.gov/api/data/"
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def _get_fast_info_value(info: dict, key_base: str):
    return (
        info.get(key_base)
        or info.get(key_base.capitalize())
        or info.get(key_base.replace("_", "").capitalize())
    )


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
    resp = requests.get(
        f"{BLS_BASE_URL}{series_id}",
        params=params,
        timeout=10,
    )
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
    """
    Return the most recently published macro indicator between CPI and NFP.
    """
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


@cached(FRED_RATE_CACHE)
def fetch_fed_rate() -> FedRate:
    """Return the latest federal funds rate from FRED."""
    if not settings.fred_api_key:
        raise RuntimeError("FRED API key missing")

    params = {
        "series_id": "FEDFUNDS",
        "api_key": settings.fred_api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }

    try:
        resp = requests.get(FRED_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        json_data = resp.json()
        obs = json_data["observations"][0]
        return FedRate(value=float(obs["value"]), date=obs["date"])
    except Exception as exc:
        FRED_RATE_CACHE.clear()
        raise RuntimeError("FRED unavailable") from exc


@cached(VIX_CACHE)
def fetch_vix() -> VIXClose:
    """Return the latest VIX closing value from FRED."""
    if not settings.fred_api_key:
        raise RuntimeError("FRED API key missing")

    params = {
        "series_id": "VIXCLS",
        "api_key": settings.fred_api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }

    try:
        resp = requests.get(FRED_BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        json_data = resp.json()
        obs = json_data["observations"][0]
        return VIXClose(value=float(obs["value"]), date=obs["date"])
    except Exception as exc:
        VIX_CACHE.clear()
        raise RuntimeError("FRED unavailable") from exc


@cached(FOMC_NEXT_CACHE)
def fetch_fomc_next() -> FomcNext | None:
    """Return the next scheduled FOMC meeting parsed from the RSS feed."""
    url = "https://www.federalreserve.gov/feeds/meetingcalendar.xml"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        xml_text = resp.text
    except Exception as exc:
        FOMC_NEXT_CACHE.clear()
        raise RuntimeError("Fed RSS unavailable") from exc

    try:
        root = ElementTree.fromstring(xml_text)
        items = root.findall(".//item")
        now = datetime.utcnow()
        for item in items:
            start_text = item.findtext("start")
            if not start_text:
                continue
            dt = datetime.fromisoformat(start_text.replace("Z", "+00:00"))
            if dt > now:
                title = item.findtext("title") or ""
                link = item.findtext("link") or ""
                return FomcNext(
                    date=dt.strftime("%Y-%m-%d"),
                    time=dt.strftime("%H:%M"),
                    title=title,
                    url=link,
                )
        return None
    except Exception as exc:
        FOMC_NEXT_CACHE.clear()
        raise RuntimeError("RSS parse error") from exc
