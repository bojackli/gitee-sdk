"""杂项资源模块。

该模块提供了Gitee API的杂项功能。
"""

from typing import Any, Dict

from gitee.resources.base import Resource


class Miscellaneous(Resource):
    """杂项资源类。

    提供Gitee API的杂项功能，如获取服务器时间、API速率限制等。
    """

    def get_server_time(self) -> Dict[str, Any]:
        """获取Gitee服务器时间。

        Returns:
            服务器时间信息
        """
        return self._get("/time")

    def get_rate_limit(self) -> Dict[str, Any]:
        """获取API速率限制信息。

        Returns:
            API速率限制信息
        """
        return self._get("/rate_limit")