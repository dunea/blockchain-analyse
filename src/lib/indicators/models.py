from pydantic import BaseModel


class Kline(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: int


class Stoch(BaseModel):
    k: float
    d: float


class StochRSI(BaseModel):
    k: float
    d: float


class MACD(BaseModel):
    macd: float
    signal: float
    hist: float


class BollingerBands(BaseModel):
    upper_band: float
    middle_band: float
    lower_band: float


class HighsLows(BaseModel):
    high: float
    low: float
