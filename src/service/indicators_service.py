from injector import inject

from src.analyst import Indicators, Kline
from src.obj import IndicatorsDto, CalculateIndicatorsRequest


class IndicatorsService:
    @inject
    def __init__(self):
        pass

    # 计算k线指标
    @staticmethod
    def calculate_indicators(request: CalculateIndicatorsRequest) -> IndicatorsDto:
        if len(request.kline_list) > 300:
            raise ValueError("计算的 K 线长度不能大于 300 个")

        indicators = Indicators([
            Kline(
                open=item.open,
                high=item.high,
                low=item.low,
                close=item.close,
                volume=item.volume,
                timestamp=item.timestamp,
            )
            for item in request.kline_list
        ])

        return IndicatorsDto(
            rsi=indicators.rsi() if request.is_rsi else None,
            stoch=indicators.stoch() if request.is_stoch else None,
            stoch_rsi=indicators.stoch_rsi() if request.is_stoch_rsi else None,
            macd=indicators.macd() if request.is_macd else None,
            adx=indicators.adx() if request.is_adx else None,
            williams_r=indicators.williams_r() if request.is_williams_r else None,
            cci=indicators.cci() if request.is_cci else None,
            atr=indicators.atr() if request.is_atr else None,
            highs_lows=indicators.highs_lows() if request.is_highs_lows else None,
            ultimate_oscillator=indicators.ultimate_oscillator() if request.is_ultimate_oscillator else None,
            roc=indicators.roc() if request.is_roc else None,
            bull_bear_power=indicators.bull_bear_power() if request.is_bull_bear_power else None,
            bollinger_bands=indicators.bollinger_bands() if request.is_bollinger_bands else None,
            ma5=indicators.ma(5) if request.is_ma5 else None,
            ma10=indicators.ma(10) if request.is_ma10 else None,
            ma20=indicators.ma(20) if request.is_ma20 else None,
            ma50=indicators.ma(50) if request.is_ma50 else None,
            ma100=indicators.ma(100) if request.is_ma100 else None,
            ma200=indicators.ma(200) if request.is_ma200 else None,
        )
