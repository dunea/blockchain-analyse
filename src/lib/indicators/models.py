from typing import Optional

from pydantic import BaseModel


class Kline(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: int


class Stoch(BaseModel):
    k: Optional[float]
    d: Optional[float]


class StochRSI(BaseModel):
    k: Optional[float]
    d: Optional[float]


class MACD(BaseModel):
    macd: Optional[float]
    signal: Optional[float]
    hist: Optional[float]


class BollingerBands(BaseModel):
    upper_band: Optional[float]
    middle_band: Optional[float]
    lower_band: Optional[float]


class HighsLows(BaseModel):
    high: Optional[float]
    low: Optional[float]
