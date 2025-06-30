from pydantic import BaseModel
from datetime import datetime


class Indicator(BaseModel):
    symbol: str
    value: float
    unit: str
    last_updated_utc: datetime


class MarketIndices(BaseModel):
    dxy_proxy_uup: Indicator
    volume_aggregated: Indicator


class MacroStat(BaseModel):
    name: str
    value: float
    unit: str
    date: str
    source: str


class PCEStat(BaseModel):
    name: str
    value: float
    unit: str
    date: str
    source: str


class LatestMacro(BaseModel):
    latest_macro: MacroStat


class FedRate(BaseModel):
    value: float
    date: str
    source: str = "FRED"


class VIXClose(BaseModel):
    value: float
    date: str
    source: str = "FRED"


class FomcNext(BaseModel):
    """Represent the next scheduled FOMC meeting."""

    date: str  # YYYY-MM-DD
    time: str  # HH:MM (UTC)
    title: str
    url: str
