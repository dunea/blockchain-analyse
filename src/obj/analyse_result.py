from typing import Literal, Optional

from pydantic import BaseModel, Field


class SwapDirection(BaseModel):
    signal: Literal['buy', 'sell', 'hold'] = Field(..., description="买卖信号")
    reason: str = Field(..., description="分析理由")
    confidence: Literal['high', 'medium', 'low'] = Field(..., description="信心")
    trend: Literal['rising', 'falling', 'sideways', 'strong_rising', 'strong_falling'] = Field(..., description="趋势")


class SwapTimeFramesDirection(SwapDirection):
    timeframe: str


class SwapStopLossTakeProfit(BaseModel):
    stop_loss: float = Field(..., description="止损价格")
    take_profit: float = Field(..., description="止盈价格")
    reason: str = Field(..., description="分析理由")
    confidence: Literal['high', 'medium', 'low'] = Field(..., description="信心")


class SwapTimeFramesStopLossTakeProfit(SwapStopLossTakeProfit):
    timeframe: str
