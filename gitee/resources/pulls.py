"""Pull Requests资源模块。

该模块提供了与Gitee Pull Requests相关的API功能。
"""

from typing import Any, Dict, List, Optional, Union

from gitee.resources.base import PaginatedList, Resource
from gitee.utils import filter_none_values, validate_required_params


class PullRequests(Resource):
    """Pull Requests资源类。

    提供与Gitee Pull Requests相关的API功能。
    """

    def list(
        self,
        owner: str,
        repo: str,
        state: Optional[str] = None,
        head: Optional[str] = None,
        base: Optional[str] = None,
        sort: Optional[str] = None,
        direction: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """获取Pull Requests列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            state: PR状态，可选值：open, closed, merged, all
            head: 包含分支名称的用户名，格式：username:branch
            base: 目标分支名称
            sort: 排序字段，可选值：created, updated, popularity, long-running
            direction: 排序方向，可选值：asc, desc
            page: 页码
            per_page: 每页数量
            **kwargs: 其他参数

        Returns:
            Pull Requests列表
        """
        validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
        params = filter_none_values(
            {
                "state": state,
                "head": head,
                "base": base,
                "sort": sort,
                "direction": direction,
                "page": page,
                "per_page": per_page,
                **kwargs,
            }
        )
        return self._get(f"/repos/{owner}/{repo}/pulls", params=params)

    def get(
        self, owner: str, repo: str, number: Union[int, str]
    ) -> Dict[str, Any]:
        """获取Pull Request详情。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Pull Request编号

        Returns:
            Pull Request详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "number": number},
            ["owner", "repo", "number"],
        )
        return self._get(f"/repos/{owner}/{repo}/pulls/{number}")

    def create(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None,
        draft: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """创建Pull Request。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            title: Pull Request标题
            head: 包含分支名称的用户名，格式：username:branch
            base: 目标分支名称
            body: Pull Request内容
            draft: 是否为草稿
            **kwargs: 其他参数

        Returns:
            创建的Pull Request详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "title": title, "head": head, "base": base},
            ["owner", "repo", "title", "head", "base"],
        )
        data = filter_none_values(
            {
                "title": title,
                "head": head,
                "base": base,
                "body": body,
                "draft": draft,
                **kwargs,
            }
        )
        return self._post(f"/repos/{owner}/{repo}/pulls", json=data)

    def update(
        self,
        owner: str,
        repo: str,
        number: Union[int, str],
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        base: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """更新Pull Request。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Pull Request编号
            title: Pull Request标题
            body: Pull Request内容
            state: PR状态，可选值：open, closed
            base: 目标分支名称
            **kwargs: 其他参数

        Returns:
            更新后的Pull Request详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "number": number},
            ["owner", "repo", "number"],
        )
        data = filter_none_values(
            {
                "title": title,
                "body": body,
                "state": state,
                "base": base,
                **kwargs,
            }
        )
        return self._patch(f"/repos/{owner}/{repo}/pulls/{number}", json=data)

    def merge(
        self,
        owner: str,
        repo: str,
        number: Union[int, str],
        merge_method: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """合并Pull Request。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Pull Request编号
            merge_method: 合并方式，可选值：merge, squash, rebase
            **kwargs: 其他参数

        Returns:
            合并结果
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "number": number},
            ["owner", "repo", "number"],
        )
        data = filter_none_values({"merge_method": merge_method, **kwargs})
        return self._put(f"/repos/{owner}/{repo}/pulls/{number}/merge", json=data)

    def list_commits(
        self,
        owner: str,
        repo: str,
        number: Union[int, str],
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取Pull Request提交列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Pull Request编号
            page: 页码
            per_page: 每页数量

        Returns:
            提交列表
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "number": number},
            ["owner", "repo", "number"],
        )
        params = filter_none_values({"page": page, "per_page": per_page})
        return self._get(f"/repos/{owner}/{repo}/pulls/{number}/commits", params=params)

    def list_files(
        self,
        owner: str,
        repo: str,
        number: Union[int, str],
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取Pull Request文件列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Pull Request编号
            page: 页码
            per_page: 每页数量

        Returns:
            文件列表
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "number": number},
            ["owner", "repo", "number"],
        )
        params = filter_none_values({"page": page, "per_page": per_page})
        return self._get(f"/repos/{owner}/{repo}/pulls/{number}/files", params=params)

    def list_comments(
        self,
        owner: str,
        repo: str,
        number: Union[int, str],
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取Pull Request评论列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Pull Request编号
            page: 页码
            per_page: 每页数量

        Returns:
            评论列表
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "number": number},
            ["owner", "repo", "number"],
        )
        params = filter_none_values({"page": page, "per_page": per_page})
        return self._get(f"/repos/{owner}/{repo}/pulls/{number}/comments", params=params)

    def create_comment(
        self,
        owner: str,
        repo: str,
        number: Union[int, str],
        body: str,
        commit_id: Optional[str] = None,
        path: Optional[str] = None,
        position: Optional[int] = None,
    ) -> Dict[str, Any]:
        """创建Pull Request评论。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Pull Request编号
            body: 评论内容
            commit_id: 提交ID
            path: 文件路径
            position: 文件中的位置

        Returns:
            创建的评论详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "number": number, "body": body},
            ["owner", "repo", "number", "body"],
        )
        data = filter_none_values(
            {
                "body": body,
                "commit_id": commit_id,
                "path": path,
                "position": position,
            }
        )
        return self._post(f"/repos/{owner}/{repo}/pulls/{number}/comments", json=data)