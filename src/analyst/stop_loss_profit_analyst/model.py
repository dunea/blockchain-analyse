from typing import Literal, Optional

from pydantic import BaseModel, Field


class StopLossProfit(BaseModel):
    stop_loss: float = Field(..., description="止损价格")
    take_profit: float = Field(..., description="止盈价格")
    reason: str = Field(..., description="分析理由")
    confidence: Literal['high', 'medium', 'low'] = Field(..., description="信心")


class TimeFramesStopLossProfit(StopLossProfit):
    timeframe: str = Field(..., description="k线周期，5m,15m,30m,1h,4h,1d")
