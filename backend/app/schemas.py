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


class LatestMacro(BaseModel):
    latest_macro: MacroStat
