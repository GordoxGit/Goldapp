from datetime import datetime
from cachetools import cached, TTLCache
import yfinance as yf

from .config import settings
from .schemas import MarketIndices, Indicator

CACHE = TTLCache(maxsize=8, ttl=settings.ttl)


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
