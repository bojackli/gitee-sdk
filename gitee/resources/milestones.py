"""里程碑资源模块。

该模块提供了与Gitee仓库里程碑相关的API功能。
"""

from typing import Any, Dict, List

from gitee.resources.base import Resource
from gitee.utils import validate_required_params


class Milestones(Resource):
    """里程碑资源类。

    提供与Gitee仓库里程碑相关的API功能，包括获取、创建、更新和删除里程碑等操作。
    """

    def list_milestones(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """获取仓库的所有里程碑。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            **kwargs: 其他可选参数

        Returns:
            里程碑列表
        """
        validate_required_params({"owner": owner, "repo": repo},
                               ["owner", "repo"])
        return self._get(f"/repos/{owner}/{repo}/milestones", params=kwargs)

    def get_milestone(self, owner: str, repo: str, number: int) -> Dict[str, Any]:
        """获取单个里程碑。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            number: 里程碑编号

        Returns:
            里程碑信息
        """
        validate_required_params({"owner": owner, "repo": repo, "number": number},
                               ["owner", "repo", "number"])
        return self._get(f"/repos/{owner}/{repo}/milestones/{number}")

    def create_milestone(self, owner: str, repo: str, title: str,
                        state: str = None, description: str = None,
                        due_on: str = None) -> Dict[str, Any]:
        """创建里程碑。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            title: 里程碑标题
            state: 里程碑状态(open/closed)
            description: 里程碑描述
            due_on: 截止日期

        Returns:
            创建的里程碑信息
        """
        validate_required_params({"owner": owner, "repo": repo, "title": title},
                               ["owner", "repo", "title"])
        data = {"title": title}
        if state:
            data["state"] = state
        if description:
            data["description"] = description
        if due_on:
            data["due_on"] = due_on
        return self._post(f"/repos/{owner}/{repo}/milestones", json=data)

    def update_milestone(self, owner: str, repo: str, number: int,
                        title: str = None, state: str = None,
                        description: str = None,
                        due_on: str = None) -> Dict[str, Any]:
        """更新里程碑。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            number: 里程碑编号
            title: 新里程碑标题
            state: 新里程碑状态(open/closed)
            description: 新里程碑描述
            due_on: 新截止日期

        Returns:
            更新后的里程碑信息
        """
        validate_required_params({"owner": owner, "repo": repo, "number": number},
                               ["owner", "repo", "number"])
        data = {}
        if title:
            data["title"] = title
        if state:
            data["state"] = state
        if description:
            data["description"] = description
        if due_on:
            data["due_on"] = due_on
        return self._patch(f"/repos/{owner}/{repo}/milestones/{number}", json=data)

    def delete_milestone(self, owner: str, repo: str, number: int) -> None:
        """删除里程碑。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            number: 里程碑编号
        """
        validate_required_params({"owner": owner, "repo": repo, "number": number},
                               ["owner", "repo", "number"])
        self._delete(f"/repos/{owner}/{repo}/milestones/{number}")