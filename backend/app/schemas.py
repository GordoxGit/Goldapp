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
