from typing import Any, Literal

import pandas as pd
import talib
from numpy import ndarray, dtype, float64
from talib import MA_Type

from .models import Kline, Stoch, MACD, StochRSI, BollingerBands, HighsLows


class Indicators:
    def __init__(self, kline_list: list[Kline]):
        self._kline_list = sorted(kline_list, key=lambda k: k.timestamp, reverse=False)
        self.df = pd.DataFrame({
            'open': [k.open for k in self._kline_list],
            'high': [k.high for k in self._kline_list],
            'low': [k.low for k in self._kline_list],
            'close': [k.close for k in self._kline_list],
            'volume': [k.volume for k in self._kline_list],
            'timestamp': [k.timestamp for k in self._kline_list],
        })

    # 计算rsi
    def rsi(self, timeperiod=14) -> list[float]:
        rsi = talib.RSI(self.df['close'], timeperiod=timeperiod)
        return rsi.tolist()

    # 计算stoch
    def stoch(self, fastk_period=9, slowk_period=1, slowd_period=6) -> list[Stoch]:
        stoch = talib.STOCH(
            self.df['high'],
            self.df['low'],
            self.df['close'],
            fastk_period=fastk_period,
            slowk_period=slowk_period,
            slowd_period=slowd_period,
        )
        ks = stoch[0].tolist()
        ds = stoch[1].tolist()
        res_list = []
        for k, d in zip(ks, ds):
            res_list.append(Stoch(k=k, d=d))
        return res_list

    # 计算stoch_rsi
    def stoch_rsi(
            self,
            timeperiod=14,
            stoch_length=5,
            smooth_k=3,
            smooth_d=3,
            ma_type: Literal['EMA', 'SMA'] = "SMA",
    ) -> list[StochRSI]:
        """
        显式计算 StochRSI：
        1. 先计算 RSI(timeperiod)
        2. 在 RSI 上计算 %K_raw = (RSI - rolling_min(RSI, stoch_length)) /
                                   (rolling_max(RSI, stoch_length) - rolling_min(...)) * 100
        3. 对 %K_raw 进行 smooth_k 的平滑，得到 %K
        4. 对 %K 进行 smooth_d 的平滑，得到 %D

        ma_type: 'SMA' 或 'EMA'（用于 K 和 D 的平滑）
        返回 list[StochRSI]，每项为 k,d（可能包含 NaN）
        """
        import numpy as np
        # 1. RSI
        rsi = talib.RSI(self.df['close'], timeperiod=timeperiod)
        # 为后续计算方便转换为 numpy 数组
        rsi_arr = np.asarray(rsi, dtype=float)

        # 2. rolling min/max 在 RSI 上
        rsi_series = pd.Series(rsi_arr)
        lowest = rsi_series.rolling(window=stoch_length, min_periods=1).min().to_numpy()
        highest = rsi_series.rolling(window=stoch_length, min_periods=1).max().to_numpy()

        # 防止除以 0
        denom = highest - lowest
        with np.errstate(divide='ignore', invalid='ignore'):
            k_raw = (rsi_arr - lowest) / denom * 100
        # 当 denom==0 时置为 0 或 NaN（保持一致性选择 NaN）
        k_raw = np.where(np.isfinite(k_raw), k_raw, np.nan)

        # 3/4 平滑 K 和 D，可选 SMA 或 EMA
        if ma_type.upper() == 'EMA':
            k_smooth = pd.Series(k_raw).ewm(span=smooth_k, adjust=False, min_periods=1).mean().to_numpy()
            d_smooth = pd.Series(k_smooth).ewm(span=smooth_d, adjust=False, min_periods=1).mean().to_numpy()
        else:
            # 默认使用 SMA
            k_smooth = pd.Series(k_raw).rolling(window=smooth_k, min_periods=1).mean().to_numpy()
            d_smooth = pd.Series(k_smooth).rolling(window=smooth_d, min_periods=1).mean().to_numpy()

        res_list = []
        for k_val, d_val in zip(k_smooth.tolist(), d_smooth.tolist()):
            res_list.append(StochRSI(k=k_val, d=d_val))
        return res_list

    # 计算MACD(12,26)
    def macd(self, fast_period=12, slow_period=26, signal_period=9) -> list[MACD]:
        macd = talib.MACD(self.df['close'], fastperiod=fast_period, slowperiod=slow_period, signalperiod=signal_period)
        hist = macd[2].tolist()
        macds = macd[0].tolist()
        signal = macd[1].tolist()
        res_list = []
        for macd, signal, hist in zip(macds, signal, hist):
            res_list.append(MACD(macd=macd, signal=signal, hist=hist))
        return res_list

    # 计算MA
    def ma(self, timeperiod: int, ma_type=0) -> list[float]:
        ma = talib.MA(self.df['close'], timeperiod=timeperiod, matype=ma_type)
        return ma.tolist()

    # 计算ADX(14)
    def adx(self, timeperiod=14) -> list[float]:
        adx = talib.ADX(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)
        return adx.tolist()

    # 计算Williams %R(14)
    def williams_r(self, timeperiod=14) -> list[float]:
        williams_r = talib.WILLR(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)
        return williams_r.tolist()

    # 计算CCI(14)
    def cci(self, timeperiod=14) -> list[float]:
        cci = talib.CCI(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)
        return cci.tolist()

    # 计算ATR(14)
    def atr(self, timeperiod=14) -> list[float]:
        atr = talib.ATR(self.df['high'], self.df['low'], self.df['close'], timeperiod=timeperiod)
        return atr.tolist()

    # 计算Highs/Lows(14)
    def highs_lows(self, timeperiod=14) -> list[HighsLows]:
        highs = talib.MAX(self.df['high'], timeperiod=timeperiod)
        lows = talib.MIN(self.df['low'], timeperiod=timeperiod)
        res_list = []
        for high, low in zip(highs.tolist(), lows.tolist()):
            res_list.append(HighsLows(high=high, low=low))
        return res_list

    # 计算UltimateOscillator
    def ultimate_oscillator(self) -> list[float]:
        ultimate_oscillator = talib.ULTOSC(self.df['high'], self.df['low'], self.df['close'])
        return ultimate_oscillator.tolist()

    # 计算ROC
    def roc(self, timeperiod=9) -> list[float]:
        roc = talib.ROC(self.df['close'], timeperiod=timeperiod)
        return roc.tolist()

    # 计算Bull/Bear Power(13)
    def bull_bear_power(self, timeperiod=13, smooth=True, ma_type: MA_Type = MA_Type.SMA) -> list[float]:
        """
        计算 BOP（Balance Of Power）。
        - 如果 smooth 为 False 或 timeperiod <= 1，返回原始 BOP。
        - 否则对 BOP 做 timeperiod 周期的移动平均（使用 talib.MA，ma_type 可指定）。
        """
        # 原始 BOP（逐根 K 线）
        bop = talib.BOP(self.df['open'], self.df['high'], self.df['low'], self.df['close'])
        # 是否平滑
        if not smooth or (timeperiod is None) or (timeperiod <= 1):
            return bop.tolist()
        # 使用 talib.MA 对 BOP 做移动平均平滑
        bop_smooth = talib.MA(bop, timeperiod=timeperiod, matype=ma_type)
        return bop_smooth.tolist()

    # 计算Bollinger Bands
    def bollinger_bands(self, timeperiod=20, nbdevup=2, nbdevdn=2, matype=MA_Type.SMA) -> list[BollingerBands]:
        upper, middle, lower = talib.BBANDS(
            self.df['close'],
            timeperiod=timeperiod,
            nbdevup=nbdevup,
            nbdevdn=nbdevdn,
            matype=matype
        )
        uppers = upper.tolist()
        middles = middle.tolist()
        lowers = lower.tolist()
        res_list = []
        for upper_v, middle_v, lower_v in zip(uppers, middles, lowers):
            res_list.append(BollingerBands(upper_band=upper_v, middle_band=middle_v, lower_band=lower_v))
        return res_list
