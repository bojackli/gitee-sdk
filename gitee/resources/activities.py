"""活动资源模块。

该模块提供了与Gitee活动相关的API功能。
"""

from typing import Any, Dict, List, Optional

from gitee.resources.base import Resource
from gitee.utils import filter_none_values


class Activities(Resource):
    """活动资源类。

    提供与Gitee活动相关的API功能。
    """

    def list_public_events(
        self,
        username: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取公开活动事件列表。

        如果指定username，则获取该用户的公开活动事件。

        Args:
            username: 用户名
            page: 页码
            per_page: 每页数量

        Returns:
            活动事件列表
        """
        params = filter_none_values({"page": page, "per_page": per_page})
        if username:
            return self._get(f"/users/{username}/events/public", params=params)
        return self._get("/events", params=params)