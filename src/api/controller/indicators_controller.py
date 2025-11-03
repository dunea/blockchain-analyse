from fastapi import APIRouter, UploadFile, File, Path, Body

from src.di import di
from src.obj import KlineDto, IndicatorsDto, CalculateIndicatorsRequest
from src.service import IndicatorsService

indicators_controller = APIRouter()


# 计算k线指标
@indicators_controller.post("/calculate", response_model=IndicatorsDto)
async def calculate_indicators(request: CalculateIndicatorsRequest = Body(...)):
    return di.get(IndicatorsService).calculate_indicators(request)
