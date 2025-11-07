from typing import Literal, Optional

from pydantic import BaseModel, Field


class Direction(BaseModel):
    signal: Literal['buy', 'sell', 'hold'] = Field(..., description="买卖信号")
    reason: str = Field(..., description="分析理由")
    confidence: Literal['high', 'medium', 'low'] = Field(..., description="信心")
    trend: Literal['rising', 'falling', 'sideways', 'strong_rising', 'strong_falling'] = Field(..., description="趋势")


class TimeFramesDirection(Direction):
    timeframe: str = Field(..., description="k线周期，5m,15m,30m,1h,4h,1d")
