import asyncio

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from src.api.controller import indicators_controller, analyse_controller
from src.api.middlewares import exception_handler

if __name__ == '__main__':
    app = FastAPI()

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源
        allow_credentials=True,
        allow_methods=["*"],  # 允许所有HTTP方法
        allow_headers=["*"],  # 允许所有HTTP头
    )

    # 错误处理器
    app.add_exception_handler(Exception, exception_handler)

    # 将路由注册到应用中
    app.include_router(indicators_controller, prefix="/api/v1/indicators", tags=["indicators"])
    app.include_router(analyse_controller, prefix="/api/v1/analyse", tags=["analyse"])

    # 运行配置
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=9000,
        timeout_keep_alive=60 * 5,
        timeout_notify=60 * 5,
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())
