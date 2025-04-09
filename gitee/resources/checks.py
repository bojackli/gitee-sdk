"""检查资源模块。

该模块提供了与Gitee检查相关的API功能。
"""

from typing import Any, Dict, List, Optional, Union

from gitee.resources.base import Resource
from gitee.utils import filter_none_values, validate_required_params


class Checks(Resource):
    """检查资源类。

    提供与Gitee检查相关的API功能。
    """

    def list(
        self,
        owner: str,
        repo: str,
        ref: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取检查列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            ref: git引用(分支/标签/SHA)
            page: 页码
            per_page: 每页数量

        Returns:
            检查列表
        """
        validate_required_params({"owner": owner, "repo": repo, "ref": ref}, ["owner", "repo", "ref"])
        params = filter_none_values({"page": page, "per_page": per_page})
        return self._get(f"/repos/{owner}/{repo}/commits/{ref}/check-runs", params=params)

    def get(
        self,
        owner: str,
        repo: str,
        check_run_id: Union[int, str],
    ) -> Dict[str, Any]:
        """获取检查详情。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            check_run_id: 检查运行ID

        Returns:
            检查详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "check_run_id": check_run_id},
            ["owner", "repo", "check_run_id"],
        )
        return self._get(f"/repos/{owner}/{repo}/check-runs/{check_run_id}")