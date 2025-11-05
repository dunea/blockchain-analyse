from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.lib.indicators.models import StochRSI, MACD, HighsLows, BollingerBands, Stoch
from .analyse_result import SwapTimeFramesDirection, SwapDirection


class KlineDto(BaseModel):
    timestamp: int = Field(...)
    open: float = Field(...)
    high: float = Field(...)
    low: float = Field(...)
    close: float = Field(...)
    volume: float = Field(...)


class IndicatorsDto(BaseModel):
    rsi: Optional[list[Optional[float]]] = Field(default=None)
    stoch: Optional[list[Stoch]] = Field(default=None)
    stoch_rsi: Optional[list[StochRSI]] = Field(default=None)
    macd: Optional[list[MACD]] = Field(default=None)
    adx: Optional[list[Optional[float]]] = Field(default=None)
    williams_r: Optional[list[Optional[float]]] = Field(default=None)
    cci: Optional[list[Optional[float]]] = Field(default=None)
    atr: Optional[list[Optional[float]]] = Field(default=None)
    highs_lows: Optional[list[HighsLows]] = Field(default=None)
    ultimate_oscillator: Optional[list[Optional[float]]] = Field(default=None)
    roc: Optional[list[Optional[float]]] = Field(default=None)
    bull_bear_power: Optional[list[Optional[float]]] = Field(default=None)
    bollinger_bands: Optional[list[BollingerBands]] = Field(default=None)
    ma5: Optional[list[Optional[float]]] = Field(default=None)
    ma10: Optional[list[Optional[float]]] = Field(default=None)
    ma20: Optional[list[Optional[float]]] = Field(default=None)
    ma50: Optional[list[Optional[float]]] = Field(default=None)
    ma100: Optional[list[Optional[float]]] = Field(default=None)
    ma200: Optional[list[Optional[float]]] = Field(default=None)


class SwapDirectionDto(BaseModel):
    directions: list[SwapTimeFramesDirection]
    conclusion_direction: SwapDirection
