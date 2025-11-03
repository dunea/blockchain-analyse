from typing import Optional

from pydantic import BaseModel, Field

from src.obj.dto import KlineDto


class CalculateIndicatorsRequest(BaseModel):
    kline_list: list[KlineDto] = Field(..., max_length=300)
    is_rsi: Optional[bool] = Field(default=None)
    is_stoch: Optional[bool] = Field(default=None)
    is_stoch_rsi: Optional[bool] = Field(default=None)
    is_macd: Optional[bool] = Field(default=None)
    is_adx: Optional[bool] = Field(default=None)
    is_williams_r: Optional[bool] = Field(default=None)
    is_cci: Optional[bool] = Field(default=None)
    is_atr: Optional[bool] = Field(default=None)
    is_highs_lows: Optional[bool] = Field(default=None)
    is_ultimate_oscillator: Optional[bool] = Field(default=None)
    is_roc: Optional[bool] = Field(default=None)
    is_bull_bear_power: Optional[bool] = Field(default=None)
    is_bollinger_bands: Optional[bool] = Field(default=None)
    is_ma5: Optional[bool] = Field(default=None)
    is_ma10: Optional[bool] = Field(default=None)
    is_ma20: Optional[bool] = Field(default=None)
    is_ma50: Optional[bool] = Field(default=None)
    is_ma100: Optional[bool] = Field(default=None)
    is_ma200: Optional[bool] = Field(default=None)
