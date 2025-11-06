import asyncio
import os
import time

import ccxt
from ccxt.async_support import okx

from src.core import settings
from src.di import di
from src.lib.indicators import Kline
from src.obj import SwapDirection, SwapTimeFramesDirection
from src.service.analyse_okx_service import AnalyseOkxService
from src.service.analyse_service import AnalyseService

os.environ['HTTP_PROXY'] = 'http://sp321weaes:gDVljM64x6feY3lvt+@dc.decodo.com:10000'
os.environ['HTTPS_PROXY'] = 'http://sp321weaes:gDVljM64x6feY3lvt+@dc.decodo.com:10000'

exchange = ccxt.okx({
    'apiKey': settings.OKX_API_KEY,
    'secret': settings.OKX_SECRET,
})
exchange.session.proxies = {
    "http": "http://127.0.0.1:10808",
    "https": "http://127.0.0.1:10808",
}


def _transition_ohlcv(ohlcv: list[list]) -> list[Kline]:
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


analyse_svc = di.get(AnalyseService)


# 分析指定之间方向
async def analyse_assign_timeframe_direction(
        timeframe: str,
        current_price: float,
        *,
        symbol: str = "BTC/USDT:USDT",
        leverage: int = 1
) -> SwapTimeFramesDirection:
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=300)
    kline_list: list[Kline] = _transition_ohlcv(ohlcv)
    swap_direction = await analyse_svc.analyse_swap_direction(kline_list, current_price, leverage=leverage)
    return SwapTimeFramesDirection.model_validate({
        **swap_direction.model_dump(),
        "timeframe": timeframe,
    })


async def test_analyse():
    timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    directions = []
    ticker = exchange.fetch_ticker("BTC/USDT:USDT")

    for timeframe in timeframes:
        direction = await analyse_assign_timeframe_direction(
            timeframe,
            float(ticker["last"]),
            symbol="BTC/USDT:USDT",
            leverage=20,
        )
        directions.append(direction)
        print(f"分析 {timeframe} 方向结果", direction)
        print("=" * 50)

    synthesize_direction = await analyse_svc.analyse_swap_directions(directions, float(ticker["last"]), leverage=20)
    print(f"综合分析方向结果", synthesize_direction)
    print("=" * 50)


async def main():
    start_time = time.time()
    analyse_okx_svc = di.get(AnalyseOkxService)
    direction = (await analyse_okx_svc.compare_direction("BTC/USDT:USDT", leverage=20, compare=3)).conclusion_direction
    print("=" * 20, f"分析耗时 {(time.time() - start_time):.2f}s", "=" * 20)
    print(direction)


async def loop_analyse():
    while True:
        try:
            await main()
        except Exception as e:
            print("ERROR by loop_analyse", e)
        await asyncio.sleep(60 * 1)


if __name__ == '__main__':
    asyncio.run(loop_analyse())
    time.sleep(3)
