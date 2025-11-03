from datetime import datetime

from pydantic import BaseModel, Field


class KlineDto(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float
    date: datetime
