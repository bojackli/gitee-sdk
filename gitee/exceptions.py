"""异常处理模块。

该模块定义了SDK特定的异常类，用于处理API错误和其他异常情况。
"""

from typing import Optional


class GiteeException(Exception):
    """Gitee SDK基础异常类。

    所有SDK异常继承自该类。
    """

    pass


class APIError(GiteeException):
    """API错误异常。

    当Gitee API返回错误响应时抛出。

    Args:
        status_code: HTTP状态码
        error_code: 错误代码
        message: 错误消息
    """

    def __init__(self, status_code: int, error_code: str, message: str) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(f"[{status_code}] {error_code}: {message}")


class AuthenticationError(GiteeException):
    """认证错误异常。

    当认证失败时抛出。

    Args:
        message: 错误消息
    """

    def __init__(self, message: str = "Authentication failed") -> None:
        self.message = message
        super().__init__(message)


class RateLimitExceeded(GiteeException):
    """速率限制异常。

    当超出API速率限制时抛出。

    Args:
        reset_time: 速率限制重置时间
        message: 错误消息
    """

    def __init__(
        self,
        reset_time: Optional[str] = None,
        message: str = "API rate limit exceeded",
    ) -> None:
        self.reset_time = reset_time
        self.message = message
        if reset_time:
            message = f"{message} (resets at {reset_time})"
        super().__init__(message)


class ValidationError(GiteeException):
    """验证错误异常。

    当请求参数验证失败时抛出。

    Args:
        message: 错误消息
    """

    def __init__(self, message: str = "Validation failed") -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(GiteeException):
    """资源未找到异常。

    当请求的资源不存在时抛出。

    Args:
        resource: 资源类型
        resource_id: 资源ID
    """

    def __init__(self, resource: str, resource_id: str) -> None:
        self.resource = resource
        self.resource_id = resource_id
        message = f"{resource} with ID {resource_id} not found"
        super().__init__(message)