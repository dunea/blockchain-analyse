import asyncio
import traceback
from typing import Optional

from ccxt.async_support import okx
from injector import inject
from openai import AsyncOpenAI

from src.core import settings
from src.lib.indicators import Kline
from src.obj import SwapTimeFramesDirection, KlineDto, SwapDirectionDto, SwapDirection
from src.service.analyse_service import AnalyseService


class AnalyseOkxService:
    @inject
    def __init__(self, exchange: okx, analyse_svc: AnalyseService):
        self._exchange = exchange
        self._analyse_svc = analyse_svc

    @staticmethod
    def _transition_ohlcv(ohlcv: list[list]) -> list[KlineDto]:
        kline_list: list[KlineDto] = []
        for item in ohlcv:
            kline_list.append(KlineDto(
                timestamp=item[0],
                open=item[1],
                high=item[2],
                low=item[3],
                close=item[4],
                volume=item[5],
            ))
        return kline_list

    # 分析指定时间方向
    async def analyse_assign_timeframe_direction(
            self,
            timeframe: str,
            current_price: float,
            *,
            symbol: str = "BTC/USDT:USDT",
            leverage: int = 1,
            async_openai: AsyncOpenAI = None,
            openai_model: str = settings.OPENAI_MODEL,
    ) -> SwapTimeFramesDirection:
        ohlcv = await self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=300)
        kline_list: list[KlineDto] = self._transition_ohlcv(ohlcv)
        swap_direction = await self._analyse_svc.analyse_swap_direction(
            kline_list,
            current_price,
            leverage=leverage,
            async_openai=async_openai,
            openai_model=openai_model
        )
        return SwapTimeFramesDirection.model_validate({
            **swap_direction.model_dump(),
            "timeframe": timeframe,
        })

    # 分析
    async def analyse(
            self,
            symbol: str,
            *,
            leverage: int = 1,
            timeframes: list[str] = None,
            async_openai: AsyncOpenAI = None,
            openai_model: str = settings.OPENAI_MODEL,
    ) -> SwapDirectionDto:
        if timeframes is None:
            timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
        if len(timeframes) <= 0:
            raise ValueError("timeframes参数不能传入空数组")
        if leverage <= 0:
            raise ValueError("leverage参数不能传入小于等于0的值")
        symbol = symbol.strip()
        if len(symbol) <= 0:
            raise ValueError("symbol参数不能传入空字符串")

        directions: list[SwapTimeFramesDirection] = []
        conclusion_direction: Optional[SwapDirection] = None
        ticker = await self._exchange.fetch_ticker(symbol)
        current_price = float(ticker["last"])

        # 分析指定时间方向
        async def task_wrapper(timeframe: str):
            try:
                return await self.analyse_assign_timeframe_direction(
                    timeframe,
                    current_price,
                    symbol=symbol,
                    leverage=leverage,
                    async_openai=async_openai,
                    openai_model=openai_model,
                )
            except Exception as e:
                return {"timeframe": timeframe, "error": e, "traceback": traceback.format_exc()}

        tasks = [asyncio.create_task(task_wrapper(timeframe)) for timeframe in timeframes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, dict) and "error" in r:
                err = r["error"]
                if isinstance(err, BaseException):
                    raise err
                else:
                    raise Exception(err)
            elif isinstance(r, Exception):
                raise r
            else:
                directions.append(r)

        # 分析最终方向
        if len(directions) >= 2:
            conclusion_direction = await self._analyse_svc.analyse_swap_directions(
                directions,
                current_price,
                leverage=leverage,
                async_openai=async_openai,
                openai_model=openai_model,
            )

        return SwapDirectionDto(
            directions=directions,
            conclusion_direction=conclusion_direction or directions[0]
        )

    # 比较分析
    async def analyse_compare(
            self,
            symbol: str,
            *,
            leverage: int = 1,
            timeframes: list[str] = None,
            compare: int = 3,
            async_openai: AsyncOpenAI = None,
            openai_model: str = settings.OPENAI_MODEL,
    ) -> SwapDirectionDto:
        analyse_result_list: list[SwapDirectionDto] = []

        async def task_wrapper():
            try:
                return await self.analyse(
                    symbol,
                    leverage=leverage,
                    timeframes=timeframes,
                    async_openai=async_openai,
                    openai_model=openai_model,
                )
            except Exception as e:
                return {"error": e, "traceback": traceback.format_exc()}

        tasks = [asyncio.create_task(task_wrapper()) for _ in range(compare)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, dict) and "error" in r:
                err = r["error"]
                if isinstance(err, BaseException):
                    raise err
                else:
                    raise Exception(err)
            elif isinstance(r, Exception):
                raise r
            else:
                analyse_result_list.append(r)

        buy_result_list: list[SwapDirectionDto] = []
        sell_result_list: list[SwapDirectionDto] = []
        hold_result_list: list[SwapDirectionDto] = []
        for result in analyse_result_list:
            if result.conclusion_direction.signal == "buy":
                buy_result_list.append(result)
            elif result.conclusion_direction.signal == "sell":
                sell_result_list.append(result)
            else:
                hold_result_list.append(result)

        # 返回数量最多的结果方向
        max_length = max(len(buy_result_list), len(sell_result_list), len(hold_result_list))
        if max_length == len(buy_result_list):
            return buy_result_list[0]
        elif max_length == len(sell_result_list):
            return sell_result_list[0]
        else:
            return hold_result_list[0]
