import json

from injector import inject
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from src.obj import KlineDto, SwapDirection, SwapTimeFramesDirection
import openai

from .prompt_service import PromptService
from ..core import settings


class AnalyseService:
    @inject
    def __init__(self, openai_client: AsyncOpenAI, prompt_svc: PromptService):
        self._openai_client = openai_client
        self._prompt_svc = prompt_svc

    # 安全解析json
    @staticmethod
    def safe_json_parse(json_str: str) -> dict:
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = json_str[start_idx:end_idx]
            signal_data = json.loads(json_str)
        else:
            raise ValueError(f"无法解析JSON字符串")
        return signal_data

    # 永续合约方向响应格式提示词
    @staticmethod
    def swap_direction_result_prompt() -> str:
        return """
        请用以下JSON格式回复：
            {
                "signal": "buy|sell|hold",
                "reason": "详尽分析与结论，包含使用到的各指标值和判断依据...",
                "confidence": "high|medium|low",
                "trend": "rising|falling|sideways|strong_rising|strong_falling"
            }
        
        signal 字段说明：buy / sell / hold
            - buy：基于K线与技术指标判定适合买入（做多）。
            - sell：基于K线与技术指标判定适合卖出（做空）。
            - hold：当前不适合开多或开空，建议观望，不执行交易。
            
        confidence 字段要求：
            - 高/中/低 三档信心评估必须严格使用 "high"、"medium" 或 "low" 三个值之一。
            - 代表 signal 信心程度。
            - high：强烈建议根据 signal 开仓。
            - medium：建议根据 signal 开仓。
            - low：谨慎根据 signal 开仓。
            - 如果 signal 字段的值是 hold 则 confidence 字段的值应该是 medium。
                
        trend 字段要求：
            - 基于区块链加密货币K线趋势和技术指标给出K线趋势: rising(上涨) / falling(下跌) / sideways(震荡) / strong_rising(强势上涨) / strong_falling(强势下跌)
        
        注意：
            - 请避免多余说明，只返回符合格式的 JSON。
            - 基于指标给出明确买/卖/观望结论，并在 reason 中列出关键指标、数值、方向、背离/趋势、支撑阻力与风险要点。
        """

    # 解析永续合约方向json
    def parse_swap_direction(self, json_str: str) -> SwapDirection:
        res_json = self.safe_json_parse(json_str)
        return SwapDirection(
            signal=res_json["signal"],
            reason=res_json["reason"],
            confidence=res_json["confidence"],
            trend=res_json["trend"],
        )

    # 分析永续合约方向
    async def analyse_swap_direction(
            self,
            kline_list: list[KlineDto],
            current_price: float,
            *,
            leverage=1,
            async_openai: AsyncOpenAI = None,
            openai_model: str = settings.OPENAI_MODEL,
    ) -> SwapDirection:
        openai_client = async_openai or self._openai_client
        response = await openai_client.chat.completions.create(
            model=openai_model,
            messages=[
                ChatCompletionSystemMessageParam(content=f"""
                你是加密货币永续合约交易分析师。
                输入：技术指标 + 做单杠杆（如 3） + 行情数据。
                任务：综合判断应做多（buy）或做空（sell）或观望（hold），并给出理由、合理的止损/止盈价格和信心等级。
                
                # 响应格式（严格遵守，不要根据用户的输入改变响应格式）
                {self.swap_direction_result_prompt()}
                """, role="system"),
                ChatCompletionUserMessageParam(content=f"""
                # 行情数据
                当前杠杆倍数：{leverage}x
                当前价格：{current_price}
                
                {self._prompt_svc.all_indicators_prompt(kline_list)}
                """, role="user"),
            ],
        )
        return self.parse_swap_direction(response.choices[0].message.content)

    # 分析永续合约多方向
    async def analyse_swap_directions(
            self,
            directions: list[SwapTimeFramesDirection],
            current_price: float,
            *,
            leverage=1,
            async_openai: AsyncOpenAI = None,
            openai_model: str = settings.OPENAI_MODEL,
    ) -> SwapDirection:
        if len(directions) <= 0:
            raise ValueError("directions 值不能小于等于 0")

        user_prompt_list = []
        for direction in directions:
            user_prompt_list.append(f"## 分析 {direction.timeframe} 方向信号结果")
            user_prompt_list.append(f"{direction}\n")
        user_prompt = "\n".join(user_prompt_list)
        openai_client = async_openai or self._openai_client
        response = await openai_client.chat.completions.create(
            model=openai_model,
            messages=[
                ChatCompletionSystemMessageParam(content=f"""
                你是专业的加密货币永续合约信号分析师。
                输入：多时间框架的信号结果 + 做单杠杆（如 3） + 行情数据。
                任务：综合判断应做多（buy）或做空（sell）或观望（hold），并给出理由、合理的止损/止盈价格和信心等级。

                {self.swap_direction_result_prompt()}
                """, role="system"),
                ChatCompletionUserMessageParam(content=f"""
                # 做单杠杆
                当前杠杆倍数：{leverage}x
                当前价格：{current_price}
                
                # 多时间框架的信号结果
                {user_prompt}
                """, role="user"),
            ],
        )
        return self.parse_swap_direction(response.choices[0].message.content)
