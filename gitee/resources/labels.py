"""标签资源模块。

该模块提供了与Gitee仓库标签相关的API功能。
"""

from typing import Any, Dict, List

from gitee.resources.base import Resource
from gitee.utils import validate_required_params


class Labels(Resource):
    """标签资源类。

    提供与Gitee仓库标签相关的API功能，包括获取、创建、更新和删除标签等操作。
    """

    def list_labels(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """获取仓库的所有标签。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称

        Returns:
            标签列表
        """
        validate_required_params({"owner": owner, "repo": repo},
                               ["owner", "repo"])
        return self._get(f"/repos/{owner}/{repo}/labels")

    def get_label(self, owner: str, repo: str, name: str) -> Dict[str, Any]:
        """获取单个标签。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            name: 标签名称

        Returns:
            标签信息
        """
        validate_required_params({"owner": owner, "repo": repo, "name": name},
                               ["owner", "repo", "name"])
        return self._get(f"/repos/{owner}/{repo}/labels/{name}")

    def create_label(self, owner: str, repo: str, name: str, color: str,
                     description: str = None) -> Dict[str, Any]:
        """创建标签。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            name: 标签名称
            color: 标签颜色(十六进制)
            description: 标签描述(可选)

        Returns:
            创建的标签信息
        """
        validate_required_params({"owner": owner, "repo": repo,
                                "name": name, "color": color},
                               ["owner", "repo", "name", "color"])
        data = {"name": name, "color": color}
        if description:
            data["description"] = description
        return self._post(f"/repos/{owner}/{repo}/labels", json=data)

    def update_label(self, owner: str, repo: str, name: str,
                     new_name: str = None, color: str = None,
                     description: str = None) -> Dict[str, Any]:
        """更新标签。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            name: 当前标签名称
            new_name: 新标签名称(可选)
            color: 新标签颜色(可选)
            description: 新标签描述(可选)

        Returns:
            更新后的标签信息
        """
        validate_required_params({"owner": owner, "repo": repo, "name": name},
                               ["owner", "repo", "name"])
        data = {}
        if new_name:
            data["name"] = new_name
        if color:
            data["color"] = color
        if description:
            data["description"] = description
        return self._patch(f"/repos/{owner}/{repo}/labels/{name}", json=data)

    def delete_label(self, owner: str, repo: str, name: str) -> None:
        """删除标签。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            name: 标签名称
        """
        validate_required_params({"owner": owner, "repo": repo, "name": name},
                               ["owner", "repo", "name"])
        self._delete(f"/repos/{owner}/{repo}/labels/{name}")