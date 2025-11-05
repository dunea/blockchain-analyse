from fastapi import APIRouter, Path, Query

from src.di import di
from src.obj import SwapDirectionDto, SwapDirection
from src.service.analyse_okx_service import AnalyseOkxService

analyse_controller = APIRouter()


# 分析 okx 数据
@analyse_controller.get("/swap/okx", response_model=SwapDirection)
async def analyse_okx(
        symbol: str = Query(...),
        leverage: int = Query(default=1),
        timeframes: str = Query(default=None)
):
    analyse_okx_svc = di.get(AnalyseOkxService)
    timeframes_list = timeframes.split(",") if timeframes else None
    result = await analyse_okx_svc.analyse_compare(symbol, leverage=leverage, timeframes=timeframes_list)
    return result.conclusion_direction
