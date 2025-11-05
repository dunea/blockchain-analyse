import ccxt

from src.core import settings
from src.di import di
from src.lib.indicators import Indicators, Kline
from src.service.prompt_service import PromptService

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
    prompt_svc = di.get(PromptService)

    print(prompt_svc.rsi_prompt(indicators.rsi(14), 14))
    print(prompt_svc.stoch_prompt(indicators.stoch(fastk_period=9, slowk_period=1, slowd_period=6), 9, 1, 6))
    print(prompt_svc.stoch_rsi_prompt(indicators.stoch_rsi(14, 5, 3, 3), 14, 5, 3, 3))
    print(prompt_svc.macd_prompt(indicators.macd(12, 26, 9), 12, 26, 9))
    print(prompt_svc.ma_prompt(indicators.ma(5), 5))
    print(prompt_svc.ma_prompt(indicators.ma(10), 10))
    print(prompt_svc.ma_prompt(indicators.ma(20), 20))
    print(prompt_svc.ma_prompt(indicators.ma(50), 50))
    print(prompt_svc.ma_prompt(indicators.ma(100), 100))
    print(prompt_svc.ma_prompt(indicators.ma(200), 200))
    print(prompt_svc.adx_prompt(indicators.adx(14), 14))
    print(prompt_svc.williams_r_prompt(indicators.williams_r(14), 14))
    print(prompt_svc.cci_prompt(indicators.cci(14), 14))
    print(prompt_svc.atr_prompt(indicators.atr(14), 14))
    print(prompt_svc.highs_lows_prompt(indicators.highs_lows(14), 14))
    print(prompt_svc.ultimate_oscillator_prompt(indicators.ultimate_oscillator()))
    print(prompt_svc.roc_prompt(indicators.roc(9), 9))
    print(prompt_svc.bull_bear_power_prompt(indicators.bull_bear_power(13), 13))
    print(prompt_svc.bollinger_bands_prompt(indicators.bollinger_bands(20, 2, 2), 20, 2, 2))
    print("=" * 50)
    print(prompt_svc.all_indicators_prompt(kline_list))
