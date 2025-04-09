"""代码片段资源模块。

该模块提供了与Gitee代码片段相关的API功能。
"""

from typing import Any, Dict, List

from gitee.resources.base import Resource
from gitee.utils import validate_required_params


class Gists(Resource):
    """代码片段资源类。

    提供与Gitee代码片段相关的API功能。
    """

    def list(self, **kwargs) -> List[Dict[str, Any]]:
        """获取代码片段列表。

        Args:
            **kwargs: 其他可选参数

        Returns:
            代码片段列表
        """
        return self._get("/gists", params=kwargs)

    def get(self, gist_id: str) -> Dict[str, Any]:
        """获取代码片段详情。

        Args:
            gist_id: 代码片段ID

        Returns:
            代码片段详情
        """
        validate_required_params({"gist_id": gist_id}, ["gist_id"])
        return self._get(f"/gists/{gist_id}")

    def create(self, files: Dict[str, Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """创建代码片段。

        Args:
            files: 文件内容，格式为 {"file1.txt": {"content": "file1 content"}, ...}
            **kwargs: 其他可选参数

        Returns:
            创建的代码片段信息
        """
        validate_required_params({"files": files}, ["files"])
        kwargs["files"] = files
        return self._post("/gists", json=kwargs)

    def update(self, gist_id: str, **kwargs) -> Dict[str, Any]:
        """更新代码片段。

        Args:
            gist_id: 代码片段ID
            **kwargs: 其他可选参数

        Returns:
            更新后的代码片段信息
        """
        validate_required_params({"gist_id": gist_id}, ["gist_id"])
        return self._patch(f"/gists/{gist_id}", json=kwargs)

    def delete(self, gist_id: str) -> None:
        """删除代码片段。

        Args:
            gist_id: 代码片段ID
        """
        validate_required_params({"gist_id": gist_id}, ["gist_id"])
        self._delete(f"/gists/{gist_id}")