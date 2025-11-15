from pydantic import BaseModel
from typing import Optional, List

class TickerResponse(BaseModel):
    exchange: str
    symbol: str
    timestamp: int
    bid: Optional[float]
    ask: Optional[float]
    last: Optional[float]
    info: dict

class HistoricalRequest(BaseModel):
    exchange: str
    symbol: str
    timeframe: str = "1m"
    since: Optional[int] = None
    limit: int = 100

class HistoricalPoint(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class HistoricalResponse(BaseModel):
    exchange: str
    symbol: str
    timeframe: str
    data: List[HistoricalPoint]
