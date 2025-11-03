import math
from typing import Any

# 自定义状态码常量
HTTP_500_INTERNAL_SERVER_ERROR = 500  # 服务器内部错误
HTTP_400_BAD_REQUEST = 400  # 错误的请求
HTTP_401_UNAUTHORIZED = 401  # 未授权
HTTP_403_FORBIDDEN = 403  # 禁止访问
HTTP_404_NOT_FOUND = 404  # 未找到
HTTP_405_METHOD_NOT_ALLOWED = 405  # 方法不被允许
HTTP_406_NOT_ACCEPTABLE = 406  # 不能接受的请求
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415  # 不支持的媒体类型
HTTP_429_TOO_MANY_REQUESTS = 429  # 请求过多


class APIException(Exception):
    status_code: int = HTTP_500_INTERNAL_SERVER_ERROR
    message: str = '服务器发生错误。'
    error_code: str = 'error'

    def __init__(self, message: str = None):
        super().__init__(message or self.message)


# 数据验证失败
class ValidationError(APIException):
    status_code: int = HTTP_400_BAD_REQUEST
    message: str = '无效输入。'
    error_code: str = 'invalid'
    detail: dict[str, str] = {}

    def __init__(self, detail: dict[str, str] = None, message: str = None):
        super().__init__(message or self.message)
        self.detail = detail or {}


# 解析错误
class ParseError(APIException):
    status_code: int = HTTP_400_BAD_REQUEST
    message: str = '请求格式错误。'
    error_code: str = 'parse_error'

    def __init__(self, message: str = None):
        super().__init__(message or self.message)


# 认证失败
class AuthenticationFailed(APIException):
    status_code: int = HTTP_401_UNAUTHORIZED
    message: str = '认证凭据不正确。'
    error_code: str = 'authentication_failed'

    def __init__(self, message: str = None):
        super().__init__(message or self.message)


# 认证凭证未提供
class NotAuthenticated(APIException):
    status_code: int = HTTP_401_UNAUTHORIZED
    message: str = '未提供认证凭据。'
    error_code: str = 'not_authenticated'

    def __init__(self, message: str = None):
        super().__init__(message or self.message)


# 权限不足
class PermissionDenied(APIException):
    status_code: int = HTTP_403_FORBIDDEN
    message: str = '您没有执行此操作的权限。'
    error_code: str = 'permission_denied'

    def __init__(self, message: str = None):
        super().__init__(message or self.message)


# 资源未找到
class NotFound(APIException):
    status_code: int = HTTP_404_NOT_FOUND
    message: str = '资源未找到。'
    error_code: str = 'not_found'

    def __init__(self, message: str = None):
        super().__init__(message or self.message)


# 不支持的媒体类型
class UnsupportedMediaType(APIException):
    status_code: int = HTTP_415_UNSUPPORTED_MEDIA_TYPE
    message: str = '请求中的媒体类型 "{media_type}" 不被支持。'
    error_code: str = 'unsupported_media_type'

    def __init__(self, media_type: str):
        super().__init__(self.message.format(media_type=media_type))
