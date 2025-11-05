import os

import openai
from ccxt.async_support import okx
from injector import Injector, Module, singleton, provider
from openai import AsyncOpenAI

from src.core import settings


class OpenaiClientProvider(Module):
    @singleton
    @provider
    def provide(self) -> AsyncOpenAI:
        return openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )


class OkxExchangeProvider(Module):
    @singleton
    @provider
    def provide(self) -> okx:
        return okx({
            'apiKey': settings.OKX_API_KEY,
            'secret': settings.OKX_SECRET,
            'aiohttp_trust_env': True,
        })


# 创建 Injector 实例并注入依赖
di = Injector([OpenaiClientProvider(), OkxExchangeProvider()])
