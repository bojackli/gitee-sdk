"""认证模块。

该模块提供了Gitee API认证相关的功能。
"""

from typing import Dict, Optional


class Auth:
    """认证类。

    处理API认证相关的功能，支持访问令牌认证方式。

    Args:
        token: Gitee API访问令牌
    """

    def __init__(self, token: Optional[str] = None) -> None:
        self.token = token

    def apply_auth(self, headers: Dict[str, str]) -> Dict[str, str]:
        """将认证信息应用到请求头。

        Args:
            headers: 原始请求头

        Returns:
            添加了认证信息的请求头
        """
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers