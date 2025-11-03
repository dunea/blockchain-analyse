from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.core import exceptions

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Credentials": "true",
}


class ErrorResponse(BaseModel):
    code: int
    message: str

    @classmethod
    def error(cls, code: int, message: str):
        # 实现：返回可序列化的数据结构（dict），避免返回 None 导致 JSONResponse content 错误
        return cls(code=code, message=str(message)).model_dump()


async def exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (ValueError, TypeError, KeyError, RuntimeError,)):
        return JSONResponse(
            status_code=417,
            content=ErrorResponse.error(417, str(exc)),
            headers={**CORS}
        )
    elif isinstance(exc, (TimeoutError, ConnectionError,)):
        return JSONResponse(
            status_code=400,
            content=ErrorResponse.error(417, str(exc)),
            headers={**CORS}
        )
    elif isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.error(exc.status_code, exc.detail),
            headers={**CORS}
        )
    elif isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse.error(422, "请求参数验证失败"),
            headers={**CORS}
        )
    elif isinstance(exc, exceptions.ValidationError):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.error(exc.status_code, exc.message),
            headers={**CORS}
        )
    elif isinstance(exc, (
            exceptions.APIException, exceptions.ParseError, exceptions.AuthenticationFailed,
            exceptions.NotAuthenticated, exceptions.PermissionDenied, exceptions.NotFound,
            exceptions.UnsupportedMediaType,)):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.error(exc.status_code, exc.message),
            headers={**CORS}
        )
    elif isinstance(exc, Exception):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse.error(500, exc.__str__()),
            headers={**CORS}
        )
    else:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse.error(500, "服务器内部错误，请稍后重试"),
            headers={**CORS}
        )
