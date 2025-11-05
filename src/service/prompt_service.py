from typing import Optional, Any

from injector import inject

from src.lib.indicators import Indicators
from src.lib.indicators.models import Stoch, StochRSI, MACD, HighsLows, BollingerBands, Kline
from src.obj import KlineDto


class PromptService:
    @inject
    def __init__(self):
        pass

    # float 列表提示词
    @staticmethod
    def _float_list_prompt(init_prompt_rows: list[str], float_list: list[Optional[float]], max_items: int = 60) -> str:
        prompt_rows = [*init_prompt_rows]
        value_list: list[str] = []
        for i in range(len(float_list)):
            if float_list[i] is None:
                continue
            value_list.append(f"{float_list[i]:.2f}")
            if len(value_list) >= max_items:
                break
        if len(value_list) == 0:
            prompt_rows.append("N/A")
            return '\n'.join(prompt_rows)

        prompt_rows.append(f"{','.join(value_list)}")
        return '\n'.join(prompt_rows)

    # 通用对象/值 列表提示词
    @staticmethod
    def _object_list_prompt(init_prompt_rows: list[str], items: list[Any], formatter, max_items: int = 60) -> str:
        """
        title: 提示词第一行
        header: 第二行（例如 "K,D" 或 "MACD,Signal,Hist"），可以传入空字符串
        items: 对象或数值列表，元素可为 None
        formatter: 可调用对象 f(item) -> str，将一个元素格式化为字符串（例如 "1.23,4.56"）
        max_items: 最大展示条数
        """
        prompt_rows = [*init_prompt_rows]
        value_list: list[str] = []
        for it in items:
            if it is None:
                continue
            try:
                s = formatter(it)
            except Exception:
                # 如果 formatter 失败，跳过该项
                continue
            if s is None or s == "":
                continue
            value_list.append(s)
            if len(value_list) >= max_items:
                break

        if len(value_list) == 0:
            prompt_rows.append("N/A")
            return '\n'.join(prompt_rows)

        for i in range(len(value_list)):
            prompt_rows.append(value_list[i])
        return '\n'.join(prompt_rows)

    # rsi 提示词
    def rsi_prompt(self, rsi: list[Optional[float]], timeperiod: int) -> str:
        return self._float_list_prompt([f"## 近期 RSI(timeperiod={timeperiod}) 技术指标"], rsi)

    # stoch 提示词
    def stoch_prompt(self, stoch: list[Stoch], fastk_period: int, slowk_period: int, slowd_period: int) -> str:
        return self._object_list_prompt(
            [
                f"## 近期 STOCH(fastk_period={fastk_period},slowk_period={slowk_period},slowd_period={slowd_period}) 技术指标",
                "K,D"
            ],
            stoch,
            lambda s: f"{s.k:.2f},{s.d:.2f}"
        )

    # stoch_rsi 提示词
    def stoch_rsi_prompt(
            self,
            stoch_rsi: list[StochRSI],
            timeperiod: int,
            stoch_length: int,
            smooth_k: int,
            smooth_d: int,
    ) -> str:
        return self._object_list_prompt(
            [
                f"## 近期 STOCHRSI(timeperiod={timeperiod},stoch_length={stoch_length},smooth_k={smooth_k},smooth_d={smooth_d}) 技术指标",
                "K,D"
            ],
            stoch_rsi,
            lambda s: f"{s.k:.2f},{s.d:.2f}"
        )

    # macd 提示词
    def macd_prompt(self, macd: list[MACD], fast_period: int, slow_period: int, signal_period: int) -> str:
        return self._object_list_prompt(
            [
                f"## 近期 MACD(fast_period={fast_period},slow_period={slow_period},signal_period={signal_period}) 技术指标",
                "MACD,Signal,Hist"
            ],
            macd,
            lambda s: f"{s.macd:.2f},{s.signal:.2f},{s.hist:.2f}"
        )

    # adx 提示词
    def adx_prompt(self, adx: list[Optional[float]], timeperiod: int) -> str:
        return self._float_list_prompt([f"## 近期 ADX(timeperiod={timeperiod}) 技术指标"], adx)

    # williams_r 提示词
    def williams_r_prompt(self, williams_r: list[Optional[float]], timeperiod: int) -> str:
        return self._float_list_prompt([f"## 近期 Williams %R(timeperiod={timeperiod}) 技术指标"], williams_r)

    # cci 提示词
    def cci_prompt(self, cci: list[Optional[float]], timeperiod: int) -> str:
        return self._float_list_prompt([f"## 近期 CCI(timeperiod={timeperiod}) 技术指标"], cci)

    # atr 提示词
    def atr_prompt(self, atr: list[Optional[float]], timeperiod: int) -> str:
        return self._float_list_prompt([f"## 近期 ATR(timeperiod={timeperiod}) 技术指标"], atr)

    # highs_lows 提示词
    def highs_lows_prompt(self, highs_lows: list[HighsLows], timeperiod: int) -> str:
        return self._object_list_prompt(
            [
                f"## 近期 Highs/Lows(timeperiod={timeperiod}) 技术指标",
                "High,Low"
            ],
            highs_lows,
            lambda s: f"{s.high:.2f},{s.low:.2f}"
        )

    # ultimate_oscillator 提示词
    def ultimate_oscillator_prompt(self, ultimate_oscillator: list[Optional[float]]) -> str:
        return self._float_list_prompt([f"## 近期 UltimateOscillator 技术指标"], ultimate_oscillator)

    # roc 提示词
    def roc_prompt(self, roc: list[Optional[float]], timeperiod: int) -> str:
        return self._float_list_prompt([f"## 近期 ROC(timeperiod={timeperiod}) 技术指标"], roc)

    # bull_bear_power 提示词
    def bull_bear_power_prompt(self, bull_bear_power: list[Optional[float]], timeperiod: int) -> str:
        return self._float_list_prompt([f"## 近期 Bull/Bear Power(timeperiod={timeperiod}) 技术指标"], bull_bear_power)

    # bollinger_bands 提示词
    def bollinger_bands_prompt(
            self,
            bollinger_bands: list[BollingerBands],
            timeperiod: int,
            nbdevup: int,
            nbdevdn: int
    ) -> str:
        return self._object_list_prompt(
            [
                f"## 近期 Bollinger Bands(timeperiod={timeperiod},nbdevup={nbdevup},nbdevdn={nbdevdn}) 技术指标",
                "Upper Band,Middle Band,Lower Band"
            ],
            bollinger_bands,
            lambda s: f"{s.upper_band:.2f},{s.middle_band:.2f},{s.lower_band:.2f}"
        )

    # ma 提示词
    def ma_prompt(self, ma: list[Optional[float]], timeperiod: int) -> str:
        return self._float_list_prompt([f"## 近期 MA(timeperiod={timeperiod}) 技术指标"], ma)

    # k线提示词
    @staticmethod
    def kline_prompt(kline_list: list[KlineDto]) -> str:
        sorted_kline_list = sorted(kline_list, key=lambda k: k.timestamp, reverse=True)
        prompt_rows = ["## 近期 k 线数据", "Timestamp,Open,High,Low,Close,Volume"]
        kline_rows = []
        for kline in sorted_kline_list:
            kline_rows.append(f"{kline.timestamp},{kline.open},{kline.high},{kline.low},{kline.close},{kline.volume}")
            if len(kline_rows) >= 60:
                break
        if len(kline_rows) == 0:
            prompt_rows.append("N/A")
        else:
            for i in range(len(kline_rows)):
                prompt_rows.append(kline_rows[i])
            prompt_rows.append("k 线数据是从上到下排列，上边的是最新数据。")
        return '\n'.join(prompt_rows)

    # 格式化提示词
    def format_prompt(self, prompt: str, kline_list: list[KlineDto]) -> str:
        indicators_kline_list: list[Kline] = []
        for item in kline_list:
            indicators_kline_list.append(Kline(
                timestamp=item.timestamp,
                open=item.open,
                high=item.high,
                low=item.low,
                close=item.close,
                volume=item.volume,
            ))

        indicators = Indicators(indicators_kline_list)

        if "{{kline}}" in prompt:
            prompt = prompt.replace("{{kline}}", self.kline_prompt(kline_list))
        if "{{rsi}}" in prompt:
            prompt = prompt.replace("{{rsi}}", self.rsi_prompt(indicators.rsi(14), 14))
        if "{{stoch}}" in prompt:
            prompt = prompt.replace("{{stoch}}", self.stoch_prompt(
                indicators.stoch(fastk_period=9, slowk_period=1, slowd_period=6),
                9, 1, 6))
        if "{{stoch_rsi}}" in prompt:
            prompt = prompt.replace("{{stoch_rsi}}", self.stoch_rsi_prompt(
                indicators.stoch_rsi(14, 5, 3, 3),
                14, 5, 3, 3
            ))
        if "{{macd}}" in prompt:
            prompt = prompt.replace("{{macd}}", self.macd_prompt(
                indicators.macd(12, 26, 9),
                12, 26, 9
            ))
        if "{{adx}}" in prompt:
            prompt = prompt.replace("{{adx}}", self.adx_prompt(indicators.adx(14), 14))
        if "{{williams_r}}" in prompt:
            prompt = prompt.replace("{{williams_r}}", self.williams_r_prompt(indicators.williams_r(14), 14))
        if "{{cci}}" in prompt:
            prompt = prompt.replace("{{cci}}", self.cci_prompt(indicators.cci(14), 14))
        if "{{atr}}" in prompt:
            prompt = prompt.replace("{{atr}}", self.atr_prompt(indicators.atr(14), 14))
        if "{{highs_lows}}" in prompt:
            prompt = prompt.replace("{{highs_lows}}", self.highs_lows_prompt(indicators.highs_lows(14), 14))
        if "{{ultimate_oscillator}}" in prompt:
            prompt = prompt.replace(
                "{{ultimate_oscillator}}",
                self.ultimate_oscillator_prompt(indicators.ultimate_oscillator()))
        if "{{roc}}" in prompt:
            prompt = prompt.replace("{{roc}}", self.roc_prompt(indicators.roc(9), 9))
        if "{{bull_bear_power}}" in prompt:
            prompt = prompt.replace(
                "{{bull_bear_power}}",
                self.bull_bear_power_prompt(indicators.bull_bear_power(13), 13))
        if "{{bollinger_bands}}" in prompt:
            prompt = prompt.replace("{{bollinger_bands}}", self.bollinger_bands_prompt(
                indicators.bollinger_bands(20, 2, 2),
                20, 2, 2))
        if "{{ma5}}" in prompt:
            prompt = prompt.replace("{{ma5}}", self.ma_prompt(indicators.ma(5), 5))
        if "{{ma10}}" in prompt:
            prompt = prompt.replace("{{ma10}}", self.ma_prompt(indicators.ma(10), 10))
        if "{{ma20}}" in prompt:
            prompt = prompt.replace("{{ma20}}", self.ma_prompt(indicators.ma(20), 20))
        if "{{ma50}}" in prompt:
            prompt = prompt.replace("{{ma50}}", self.ma_prompt(indicators.ma(50), 50))
        if "{{ma100}}" in prompt:
            prompt = prompt.replace("{{ma100}}", self.ma_prompt(indicators.ma(100), 100))
        if "{{ma200}}" in prompt:
            prompt = prompt.replace("{{ma200}}", self.ma_prompt(indicators.ma(200), 200))

        return prompt

    # 全部技术指标提示词
    def all_indicators_prompt(self, kline_list: list[KlineDto]) -> str:
        prompt = [
            "# 技术指标",
            "{{kline}}\n",
            "{{rsi}}\n",
            "{{stoch}}\n",
            "{{stoch_rsi}}\n",
            "{{macd}}\n",
            "{{adx}}\n",
            "{{williams_r}}\n",
            "{{cci}}\n",
            "{{atr}}\n",
            "{{highs_lows}}\n",
            "{{ultimate_oscillator}}\n",
            "{{roc}}\n",
            "{{bull_bear_power}}\n",
            "{{bollinger_bands}}\n",
            "{{ma5}}\n",
            "{{ma10}}\n",
            "{{ma20}}\n",
            "{{ma50}}\n",
            "{{ma100}}\n",
            "{{ma200}}\n",
            "技术指标是从上到下排列，从左到右排列；上下排列的上边的是最新数据，左右排列的左边的是最新数据。"
        ]
        return self.format_prompt('\n'.join(prompt), kline_list)
