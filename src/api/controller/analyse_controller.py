from typing import Literal, Optional

import openai
from fastapi import APIRouter, Path, Query, Header

from src.analyst import Direction, StopLossProfit
from src.di import di
from src.service.analyse_okx_service import AnalyseByOkxDirectionService, AnalyseByOkxStopLossProfitService

analyse_controller = APIRouter()


# 分析 okx 方向
@analyse_controller.get("/swap/okx", response_model=Direction, summary="AI 分析 okx 永续合约多空信号")
async def analyse_okx(
        symbol: str = Query(default="BTC/USDT:USDT", description="填入合约标识，例如：BTC/USDT:USDT"),
        leverage: int = Query(default=1, description="杠杆倍数，低杠杆倍数信号会更大胆，高杠杆信号会更畏缩一些"),
        timeframes: str = Query(
            default="5m,15m,1h",
            description="检查的k线周期，例如：1m,5m,15m,30m,1h,4h,1d，同时填入多个标识同时根据多个k线数据进行分析"),
        compare: int = Query(
            default=3,
            ge=1,
            le=10,
            description="对比次数，多次对比结果选择概率比较大的信号，推荐填入：3,5,7，这种奇数"),
        openai_api_key: str = Header(..., alias="OPENAI-API-KEY", description="兼容openai的apikey"),
        openai_base_url: str = Header(..., alias="OPENAI-BASE-URL", description="兼容openai的api链接"),
        openai_model: str = Header(..., alias="OPENAI-MODEL", description="兼容openai的模型"),
):
    # openai
    async_openai = openai.AsyncOpenAI(
        api_key=openai_api_key,
        base_url=openai_base_url,
    )

    # 分析
    svc = di.get(AnalyseByOkxDirectionService)
    result = await svc.compare_analyses_by_symbol(
        symbol,
        timeframes.split(","),
        async_openai,
        openai_model,
        leverage=leverage,
        compare=compare,
    )

    await async_openai.close()
    return result


# 分析 okx 止损止盈价格
@analyse_controller.get("/swap-stop-loss/okx", response_model=StopLossProfit,
                        summary="AI 分析 okx 永续合约止盈止损价格")
async def analyse_okx_stop_loss(
        symbol: str = Query(default="BTC/USDT:USDT", description="填入合约标识，例如：BTC/USDT:USDT"),
        leverage: int = Query(
            default=1,
            description="杠杆倍数，低杠杆倍数止盈/止损会更大胆，高杠杆止盈/止损会更畏缩一些"),
        direction: Literal['long', 'short'] = Query(..., description="开仓方向, long: 做多；short：做空"),
        timeframes: str = Query(
            default="5m,15m,1h",
            description="检查的k线周期，例如：1m,5m,15m,30m,1h,4h,1d，同时填入多个标识同时根据多个k线数据进行分析"),
        entry_price: Optional[float] = Query(
            default=None,
            description="如果已经持仓请填入开仓均价，更好的判断持仓的止损价格"),
        openai_api_key: str = Header(..., alias="OPENAI-API-KEY", description="兼容openai的apikey"),
        openai_base_url: str = Header(..., alias="OPENAI-BASE-URL", description="兼容openai的api链接"),
        openai_model: str = Header(..., alias="OPENAI-MODEL", description="兼容openai的模型"),
):
    # openai
    async_openai = openai.AsyncOpenAI(
        api_key=openai_api_key,
        base_url=openai_base_url,
    )

    # 分析
    svc = di.get(AnalyseByOkxStopLossProfitService)
    result = await svc.analyses_by_symbol(
        symbol,
        direction,
        timeframes.split(","),
        async_openai,
        openai_model,
        leverage=leverage,
        entry_price=entry_price,
    )

    await async_openai.close()
    return result
