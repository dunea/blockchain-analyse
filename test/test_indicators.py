import ccxt
from yfinance import data

from src.core import settings
from src.analyst.indicators import Indicators, Kline

exchange = ccxt.okx({
    'apiKey': settings.OKX_API_KEY,
    'secret': settings.OKX_SECRET,
})
exchange.session.proxies = {
    "http": "http://127.0.0.1:10809",
    "https": "http://127.0.0.1:10809",
}

if __name__ == '__main__':
    ohlcv = exchange.fetch_ohlcv("BTC/USDT:USDT", timeframe="4h", limit=300)
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

    indicators = Indicators(kline_list)

    # 计算rsi
    print("=" * 25, "计算rsi(14)", "=" * 25)
    print(indicators.rsi(14)[:5], "...")

    # 计算stoch
    print("=" * 25, "计算stoch(9,6)", "=" * 25)
    stoch_list = indicators.stoch(9, 1, 6)
    print([[stoch.k, stoch.d] for stoch in stoch_list[:5]], "...")

    # 计算stoch_rsi
    print("=" * 25, "计算stoch_rsi(14)", "=" * 25)
    stoch_rsi = indicators.stoch_rsi(14, 5, 3, 3)
    print([[v.k, v.d] for v in stoch_rsi[:5]], "...")

    # 计算macd
    print("=" * 25, "计算macd(12,26)", "=" * 25)
    macd = indicators.macd(12, 26, 9)
    print([[v.hist, v.macd, v.signal] for v in macd[:5]], "...")

    # 计算ma(5)
    print("=" * 25, "计算ma(5)", "=" * 25)
    ma = indicators.ma(5)
    print([v for v in ma[:5]], "...")

    # 计算ma(10)
    print("=" * 25, "计算ma(10)", "=" * 25)
    ma = indicators.ma(10)
    print([v for v in ma[:5]], "...")

    # 计算ma(20)
    print("=" * 25, "计算ma(20)", "=" * 25)
    ma = indicators.ma(20)
    print([v for v in ma[:5]], "...")

    # 计算ma(50)
    print("=" * 25, "计算ma(50)", "=" * 25)
    ma = indicators.ma(50)
    print([v for v in ma[:5]], "...")

    # 计算ma(100)
    print("=" * 25, "计算ma(100)", "=" * 25)
    ma = indicators.ma(100)
    print([v for v in ma[:5]], "...")

    # 计算ma(200)
    print("=" * 25, "计算ma(200)", "=" * 25)
    ma = indicators.ma(200)
    print([v for v in ma[:5]], "...")

    # 计算adx(14)
    print("=" * 25, "计算adx(14)", "=" * 25)
    ma = indicators.adx(14)
    print([v for v in ma[:5]], "...")

    # 计算Williams %R(14)
    print("=" * 25, "计算Williams %R(14)", "=" * 25)
    ma = indicators.williams_r(14)
    print([v for v in ma[:5]], "...")

    # 计算CCI(14)
    print("=" * 25, "计算CCI(14)", "=" * 25)
    ma = indicators.cci(14)
    print([v for v in ma[:5]], "...")

    # 计算ATR(14)
    print("=" * 25, "计算ATR(14)", "=" * 25)
    ma = indicators.atr(14)
    print([v for v in ma[:5]], "...")

    # 计算Highs/Lows(14)
    print("=" * 25, "计算Highs/Lows(14)", "=" * 25)
    ma = indicators.highs_lows(14)
    print([[v.high, v.low] for v in ma[:5]], "...")

    # 计算UltimateOscillator
    print("=" * 25, "计算UltimateOscillator", "=" * 25)
    ma = indicators.ultimate_oscillator()
    print([v for v in ma[:5]], "...")

    # 计算ROC
    print("=" * 25, "计算ROC(9)", "=" * 25)
    ma = indicators.roc(9)
    print([v for v in ma[:5]], "...")

    # 计算Bull/Bear Power(13)
    print("=" * 25, "计算Bull/Bear Power(13)", "=" * 25)
    ma = indicators.bull_bear_power(13)
    print([v for v in ma[:5]], "...")

    # 计算Bollinger Bands
    print("=" * 25, "计算Bollinger Bands(20,2,2)", "=" * 25)
    macd = indicators.bollinger_bands(20, 2, 2)
    print([[v.upper_band, v.lower_band, v.middle_band] for v in macd[:5]], "...")
