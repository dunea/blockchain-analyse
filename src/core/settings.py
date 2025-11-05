import os
from typing import Optional

from pydantic.v1 import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 配置
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field(..., env="OPENAI_BASE_URL")
    OPENAI_MODEL: str = Field(..., env="OPENAI_MODEL")

    # Okx
    OKX_API_KEY: str = Field(..., env="OKX_API_KEY")
    OKX_SECRET: str = Field(..., env="OKX_SECRET")

    model_config = {
        "extra": "ignore",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
