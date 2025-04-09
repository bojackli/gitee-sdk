"""邮件资源模块。

该模块提供了与Gitee邮件相关的API功能。
"""

from typing import Any, Dict, List

from gitee.resources.base import Resource
from gitee.utils import validate_required_params


class Emails(Resource):
    """邮件资源类。

    提供与Gitee邮件相关的API功能。
    """

    def list(self) -> List[Dict[str, Any]]:
        """获取当前用户的所有邮箱地址。

        Returns:
            邮箱地址列表
        """
        return self._get("/user/emails")

    def add(self, emails: List[str]) -> List[Dict[str, Any]]:
        """添加邮箱地址。

        Args:
            emails: 要添加的邮箱地址列表

        Returns:
            添加的邮箱地址列表
        """
        validate_required_params({"emails": emails}, ["emails"])
        return self._post("/user/emails", json=emails)

    def delete(self, emails: List[str]) -> None:
        """删除邮箱地址。

        Args:
            emails: 要删除的邮箱地址列表
        """
        validate_required_params({"emails": emails}, ["emails"])
        self._delete("/user/emails", json=emails)