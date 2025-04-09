"""Git数据资源模块。

该模块提供了与Gitee Git数据相关的API功能。
"""

from typing import Any, Dict, List

from gitee.resources.base import Resource
from gitee.utils import validate_required_params


class GitData(Resource):
    """Git数据资源类。

    提供与Gitee Git数据相关的API功能，包括获取提交、标签、分支等信息。
    """

    def get_commit(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """获取提交信息。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            sha: 提交的SHA值

        Returns:
            提交信息
        """
        validate_required_params({"owner": owner, "repo": repo, "sha": sha},
                               ["owner", "repo", "sha"])
        return self._get(f"/repos/{owner}/{repo}/git/commits/{sha}")

    def get_tag(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """获取标签信息。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            sha: 标签的SHA值

        Returns:
            标签信息
        """
        validate_required_params({"owner": owner, "repo": repo, "sha": sha},
                               ["owner", "repo", "sha"])
        return self._get(f"/repos/{owner}/{repo}/git/tags/{sha}")

    def list_refs(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """获取引用列表。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            **kwargs: 其他可选参数

        Returns:
            引用列表
        """
        validate_required_params({"owner": owner, "repo": repo},
                               ["owner", "repo"])
        return self._get(f"/repos/{owner}/{repo}/git/refs", params=kwargs)

    def get_ref(self, owner: str, repo: str, ref: str) -> Dict[str, Any]:
        """获取引用信息。

        Args:
            owner: 仓库所属用户/组织
            repo: 仓库名称
            ref: 引用名称

        Returns:
            引用信息
        """
        validate_required_params({"owner": owner, "repo": repo, "ref": ref},
                               ["owner", "repo", "ref"])
        return self._get(f"/repos/{owner}/{repo}/git/refs/{ref}")