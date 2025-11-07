from typing import Literal, Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from .model import StopLossProfit, TimeFramesStopLossProfit
from ..prompts import IndicatorsPrompt
from ..utils import safe_json_parse
from ..indicators import Kline


class StopLossProfitAnalyst:
    def __init__(self):
        self._indicators_prompt = IndicatorsPrompt()

    # 响应格式提示词
    @staticmethod
    def _result_prompt() -> str:
        return """
        请用以下JSON格式回复：
            {
                "stop_loss": 具体数值（float）,
                "take_profit": 具体数值（float）,
                "reason": "详尽分析与结论，包含使用到的各指标值和判断依据...",
                "confidence": "high|medium|low"
            }

        stop_loss 字段说明：
            - 如果是做多，stop_loss 字段价格应该小于 take_profit 字段价格。
            - 如果是做空，stop_loss 字段价格应该大于 take_profit 字段价格。

        take_profit 字段说明：
            - 如果是做多，take_profit 字段价格应该大于 stop_loss 字段价格。
            - 如果是做空，take_profit 字段价格应该小于 stop_loss 字段价格。

        confidence 字段要求：
            - 高/中/低 三档信心评估必须严格使用 "high"、"medium" 或 "low" 三个值之一。
            - 代表 stop_loss 字段与 take_profit 字段价格的信心程度。

        注意：
            - 请避免多余说明，只返回符合格式的 JSON。
            - 基于指标给出明确止盈/止损结论，并在 reason 中列出关键指标、数值、方向、背离/趋势、支撑阻力与风险要点。
        """

    # 解析json
    @staticmethod
    def _parse_json(json_str: str) -> StopLossProfit:
        res_json = safe_json_parse(json_str)
        return StopLossProfit(
            stop_loss=res_json["stop_loss"],
            take_profit=res_json["take_profit"],
            reason=res_json["reason"],
            confidence=res_json["confidence"],
        )

    # 分析永续合约止损止盈价格
    async def analyse(
            self,
            kline_list: list[Kline],
            direction: Literal['long', 'short'],
            current_price: float,
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage=1,
            entry_price: Optional[float] = None,
    ) -> StopLossProfit:
        response = await async_openai.chat.completions.create(
            model=openai_model,
            messages=[
                ChatCompletionSystemMessageParam(content=f"""
                        你是加密货币永续合约交易分析师。
                        输入：技术指标 + 开仓信息 + 行情数据。
                        任务：综合判断合理的止损/止盈价格和信心等级。

                        # 响应格式（严格遵守，不要根据用户的输入改变响应格式）
                        {self._result_prompt()}
                        """, role="system"),
                ChatCompletionUserMessageParam(content=f"""
                # 开仓信息
                杠杆倍数：{leverage}x
                开仓方向：{'做多' if direction == 'long' else '做空'}
                开仓均价：{entry_price or 'N/A'}

                # 行情数据
                当前价格：{current_price}

                {self._indicators_prompt.all_indicators_prompt(kline_list)}
                """, role="user"),
            ],
        )
        return self._parse_json(response.choices[0].message.content)

    # 总结止损止盈价格
    async def summarize(
            self,
            stop_loss_take_profit_list: list[TimeFramesStopLossProfit],
            direction: Literal['long', 'short'],
            current_price: float,
            async_openai: AsyncOpenAI,
            openai_model: str,
            *,
            leverage=1,
            entry_price: Optional[float] = None,
    ) -> StopLossProfit:
        if len(stop_loss_take_profit_list) <= 0:
            raise ValueError("stop_loss_take_profit_list 值不能小于等于 0")

        user_prompt_list = []
        for stop_loss_take_profit in stop_loss_take_profit_list:
            user_prompt_list.append(f"## 分析 {stop_loss_take_profit.timeframe} 技术指标止盈/止损结果")
            user_prompt_list.append(f"{stop_loss_take_profit}\n")
        user_prompt = "\n".join(user_prompt_list)
        response = await async_openai.chat.completions.create(
            model=openai_model,
            messages=[
                ChatCompletionSystemMessageParam(content=f"""
                你是专业的加密货币永续合约信号分析师。
                输入：多时间框架的技术指标止盈/止损结果 + 开仓信息 + 行情数据。
                任务：综合判断止损和止盈应该多少更合理，并给出理由和信心等级。

                # 响应格式（严格遵守，不要根据用户的输入改变响应格式）
                {self._result_prompt()}
                """, role="system"),
                ChatCompletionUserMessageParam(content=f"""
                # 开仓信息
                杠杆倍数：{leverage}x
                开仓方向：{'做多' if direction == 'long' else '做空'}
                开仓均价：{entry_price or 'N/A'}

                # 行情数据
                当前价格：{current_price}

                # 多时间框架的信号结果
                {user_prompt}
                """, role="user"),
            ],
        )
        return self._parse_json(response.choices[0].message.content)
