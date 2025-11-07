import asyncio
import traceback
from typing import Optional, Literal, Any, Coroutine

from ccxt.async_support import okx
from injector import inject
from openai import AsyncOpenAI

from src.analyst import Kline, TimeFramesDirection, DirectionAnalyst, Direction, StopLossProfitAnalyst, StopLossProfit, \
    TimeFramesStopLossProfit
from src.core import settings
from src.obj import KlineDto, SwapDirectionDto


# 转换ohlcv
def transition_ohlcv(ohlcv: list[list]) -> list[Kline]:
    kline_list: list[Kline] = []
    for item in ohlcv:
        kline_list.append(Kline(
            timestamp=item[0],
            open=item[1],
            high=item[2],
            low=item[3],
            close=item[4],
            volume=item[5],
        ))
    return kline_list


# 并发执行异步
async def run_coroutines(tasks: list[Coroutine[Any, Any, Any]], return_exceptions=True) -> list[Any]:
    # 转换为 task 任务列表
    async def _task(task: Coroutine[Any, Any, Any], params: dict):
        try:
            return await task
        except Exception as e:
            return {**params, "error": e, "traceback": traceback.format_exc()}

    task_list = []
    for task in tasks:
        task_list.append(
            asyncio.create_task(task)
        )

    results = await asyncio.gather(*task_list, return_exceptions=return_exceptions)

    output = []
    for result in results:
        if isinstance(result, dict) and "error" in result:
            error = result["error"]
            if isinstance(error, BaseException):
                raise error
            raise Exception(error)
        if isinstance(result, Exception):
            raise result
        output.append(result)

    return output


class AnalyseDirection:
    def __init__(self):
        self._direction_analyst = DirectionAnalyst()

    # 分析
    async def analyse(
            self,
            kline_list: list[Kline],
            current_price: float,
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage: int = 1
    ) -> Direction:
        if leverage <= 0:
            raise ValueError("leverage参数不能传入小于等于0的值")

        return await self._direction_analyst.analyse(
            kline_list,
            current_price,
            async_openai,
            openai_model,
            leverage=leverage,
        )

    # 分析多k线
    async def analyses(
            self,
            directions: list[TimeFramesDirection],
            current_price: float,
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage: int = 1
    ) -> Direction:
        if leverage <= 0:
            raise ValueError("leverage参数不能传入小于等于0的值")
        if len(directions) <= 0:
            raise ValueError("directions参数不能传入小于等于0的长度")

        # 分析最终方向
        conclusion_direction = None
        if len(directions) >= 2:
            conclusion_direction = await self._direction_analyst.summarize(
                directions,
                current_price,
                async_openai,
                openai_model,
                leverage=leverage,
            )

        return conclusion_direction or directions[0]

    # 比较分析多k线
    @staticmethod
    async def compare_analyses(directions: list[Direction]) -> Direction:
        buy_result_list: list[Direction] = []
        sell_result_list: list[Direction] = []
        hold_result_list: list[Direction] = []
        for result in directions:
            if result.signal == "buy":
                buy_result_list.append(result)
            elif result.signal == "sell":
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


class AnalyseStopLossProfit:
    def __init__(self):
        self._stop_loss_profit_analyst = StopLossProfitAnalyst()

    # 分析
    async def analyse(
            self,
            kline_list: list[Kline],
            direction: Literal['long', 'short'],
            current_price: float,
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage: int = 1,
            entry_price: Optional[float] = None
    ) -> StopLossProfit:
        if leverage <= 0:
            raise ValueError("leverage参数不能传入小于等于0的值")

        return await self._stop_loss_profit_analyst.analyse(
            kline_list,
            direction,
            current_price,
            async_openai,
            openai_model,
            leverage=leverage,
            entry_price=entry_price,
        )

    # 分析多k线
    async def analyses(
            self,
            stop_loss_profits: list[TimeFramesStopLossProfit],
            direction: Literal['long', 'short'],
            current_price: float,
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage: int = 1,
            entry_price: Optional[float] = None,
    ) -> StopLossProfit:
        if leverage <= 0:
            raise ValueError("leverage参数不能传入小于等于0的值")
        if len(stop_loss_profits) <= 0:
            raise ValueError("stop_loss_profits参数不能传入小于等于0的长度")

        # 总结止损止盈价格
        conclusion = None
        if len(stop_loss_profits) >= 2:
            conclusion = await self._stop_loss_profit_analyst.summarize(
                stop_loss_profits,
                direction,
                current_price,
                async_openai,
                openai_model,
                leverage=leverage,
                entry_price=entry_price,
            )

        return conclusion or stop_loss_profits[0]


class AnalyseByOkxDirectionService(AnalyseDirection):
    @inject
    def __init__(self, exchange: okx):
        super().__init__()
        self._exchange = exchange

    async def analyse_by_symbol(
            self,
            symbol: str,
            timeframe: str,
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage: int = 1,
            current_price: Optional[float] = None,
    ) -> Direction:
        symbol = symbol.strip()
        timeframe = timeframe.strip()
        if len(symbol) <= 0:
            raise ValueError("symbol值不能为空")
        if leverage <= 0:
            raise ValueError("leverage值不能小于等于0")
        if len(timeframe) <= 0:
            raise ValueError("timeframe值不能为空")

        ohlcv = await self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=300)
        kline_list = transition_ohlcv(ohlcv)

        if current_price is None:
            ticker = await self._exchange.fetch_ticker(symbol)
            current_price = float(ticker["last"])

        return await self.analyse(kline_list, current_price, async_openai, openai_model, leverage=leverage)

    async def analyses_by_symbol(
            self,
            symbol: str,
            timeframes: list[str],
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage: int = 1,
            current_price: Optional[float] = None,
    ) -> Direction:
        symbol = symbol.strip()
        if len(symbol) <= 0:
            raise ValueError("symbol值不能为空")
        if leverage <= 0:
            raise ValueError("leverage值不能小于等于0")
        if timeframes is None or len(timeframes) <= 0:
            raise ValueError("timeframes值不能为空")

        async def task_wrapper(timeframe: str) -> TimeFramesDirection:
            r = await self.analyse_by_symbol(symbol, timeframe, async_openai, openai_model, leverage=leverage)
            return TimeFramesDirection.model_validate({
                **r.model_dump(),
                "timeframe": timeframe,
            })

        analytics: list[TimeFramesDirection] = await run_coroutines([
            task_wrapper(timeframe) for timeframe in timeframes])

        if current_price is None:
            ticker = await self._exchange.fetch_ticker(symbol)
            current_price = float(ticker["last"])

        return await self.analyses(analytics, current_price, async_openai, openai_model, leverage=leverage)

    async def compare_analyses_by_symbol(
            self,
            symbol: str,
            timeframes: list[str],
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage: int = 1,
            compare: int = 3,
    ) -> Direction:
        symbol = symbol.strip()
        if len(symbol) <= 0:
            raise ValueError("symbol值不能为空")
        if leverage <= 0:
            raise ValueError("leverage值不能小于等于0")
        if compare <= 0:
            raise ValueError("compare值不能小于等于0")
        if timeframes is None or len(timeframes) <= 0:
            raise ValueError("timeframes值不能为空")

        # 获取 symbol 当前价格
        ticker = await self._exchange.fetch_ticker(symbol)
        current_price = float(ticker["last"])

        # 并发获取分析结果
        analytics: list[Direction] = await run_coroutines([
            self.analyses_by_symbol(symbol, timeframes, async_openai, openai_model, leverage=leverage,
                                    current_price=current_price)
            for _ in range(compare)
        ])

        return await self.compare_analyses(analytics)


class AnalyseByOkxStopLossProfitService(AnalyseStopLossProfit):
    @inject
    def __init__(self, exchange: okx):
        super().__init__()
        self._exchange = exchange

    async def analyse_by_symbol(
            self,
            symbol: str,
            direction: Literal['long', 'short'],
            timeframe: str,
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage: int = 1,
            current_price: Optional[float] = None,
            entry_price: Optional[float] = None,
    ) -> StopLossProfit:
        symbol = symbol.strip()
        timeframe = timeframe.strip()
        if len(symbol) <= 0:
            raise ValueError("symbol值不能为空")
        if leverage <= 0:
            raise ValueError("leverage值不能小于等于0")
        if len(timeframe) <= 0:
            raise ValueError("timeframe值不能为空")

        ohlcv = await self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=300)
        kline_list = transition_ohlcv(ohlcv)

        if current_price is None:
            ticker = await self._exchange.fetch_ticker(symbol)
            current_price = float(ticker["last"])

        return await self.analyse(kline_list, direction, current_price, async_openai, openai_model, leverage=leverage,
                                  entry_price=entry_price)

    async def analyses_by_symbol(
            self,
            symbol: str,
            direction: Literal['long', 'short'],
            timeframes: list[str],
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage: int = 1,
            current_price: Optional[float] = None,
            entry_price: Optional[float] = None,
    ) -> StopLossProfit:
        symbol = symbol.strip()
        if len(symbol) <= 0:
            raise ValueError("symbol值不能为空")
        if leverage <= 0:
            raise ValueError("leverage值不能小于等于0")
        if timeframes is None or len(timeframes) <= 0:
            raise ValueError("timeframes值不能为空")

        async def task_wrapper(timeframe: str) -> TimeFramesStopLossProfit:
            r = await self.analyse_by_symbol(symbol, direction, timeframe, async_openai, openai_model,
                                             leverage=leverage, entry_price=entry_price)
            return TimeFramesStopLossProfit.model_validate({
                **r.model_dump(),
                "timeframe": timeframe,
            })

        analytics: list[TimeFramesStopLossProfit] = await run_coroutines([
            task_wrapper(timeframe) for timeframe in timeframes])

        if current_price is None:
            ticker = await self._exchange.fetch_ticker(symbol)
            current_price = float(ticker["last"])
        return await self.analyses(analytics, direction, current_price, async_openai, openai_model, leverage=leverage,
                                   entry_price=entry_price)
