"""Issues资源模块。

该模块提供了与Gitee Issues相关的API功能。
"""

from typing import Any, Dict, List, Optional, Union

from gitee.resources.base import PaginatedList, Resource
from gitee.utils import filter_none_values, validate_required_params


class Issues(Resource):
    """Issues资源类。

    提供与Gitee Issues相关的API功能。
    """

    def list(
        self,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[str] = None,
        sort: Optional[str] = None,
        direction: Optional[str] = None,
        since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """获取Issues列表。

        如果指定了owner和repo，则获取指定仓库的Issues列表；
        否则获取当前用户的Issues列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            state: Issue状态，可选值：open, closed, all
            labels: 标签，多个标签用逗号分隔
            sort: 排序字段，可选值：created, updated, comments
            direction: 排序方向，可选值：asc, desc
            since: 起始时间，ISO 8601格式
            page: 页码
            per_page: 每页数量
            **kwargs: 其他参数

        Returns:
            Issues列表
        """
        params = filter_none_values(
            {
                "state": state,
                "labels": labels,
                "sort": sort,
                "direction": direction,
                "since": since,
                "page": page,
                "per_page": per_page,
                **kwargs,
            }
        )

        if owner and repo:
            validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
            url = f"/repos/{owner}/{repo}/issues"
        else:
            url = "/issues"

        return self._get(url, params=params)

    def get(
        self, owner: str, repo: str, number: Union[int, str]
    ) -> Dict[str, Any]:
        """获取Issue详情。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Issue编号

        Returns:
            Issue详情
        """
        return self._get(f"/repos/{owner}/{repo}/issues/{number}")

    def create(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        assignee: Optional[str] = None,
        milestone: Optional[int] = None,
        labels: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """创建Issue。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            title: Issue标题
            body: Issue内容
            assignee: 指派给的用户
            milestone: 里程碑ID
            labels: 标签列表
            **kwargs: 其他参数

        Returns:
            创建的Issue详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "title": title},
            ["owner", "repo", "title"],
        )
        data = filter_none_values(
            {
                "title": title,
                "body": body,
                "assignee": assignee,
                "milestone": milestone,
                "labels": labels,
                **kwargs,
            }
        )
        return self._post(f"/repos/{owner}/{repo}/issues", json=data)

    def update(
        self,
        owner: str,
        repo: str,
        number: Union[int, str],
        title: Optional[str] = None,
        body: Optional[str] = None,
        assignee: Optional[str] = None,
        milestone: Optional[int] = None,
        labels: Optional[List[str]] = None,
        state: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """更新Issue。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Issue编号
            title: Issue标题
            body: Issue内容
            assignee: 指派给的用户
            milestone: 里程碑ID
            labels: 标签列表
            state: Issue状态，可选值：open, closed, progressing
            **kwargs: 其他参数

        Returns:
            更新后的Issue详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "number": number},
            ["owner", "repo", "number"],
        )
        data = filter_none_values(
            {
                "title": title,
                "body": body,
                "assignee": assignee,
                "milestone": milestone,
                "labels": labels,
                "state": state,
                **kwargs,
            }
        )
        return self._patch(f"/repos/{owner}/{repo}/issues/{number}", json=data)

    def list_comments(
        self,
        owner: str,
        repo: str,
        number: Union[int, str],
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取Issue评论列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Issue编号
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
        return self._get(f"/repos/{owner}/{repo}/issues/{number}/comments", params=params)

    def create_comment(
        self, owner: str, repo: str, number: Union[int, str], body: str
    ) -> Dict[str, Any]:
        """创建Issue评论。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            number: Issue编号
            body: 评论内容

        Returns:
            创建的评论详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "number": number, "body": body},
            ["owner", "repo", "number", "body"],
        )
        data = {"body": body}
        return self._post(f"/repos/{owner}/{repo}/issues/{number}/comments", json=data)

    def update_comment(
        self, owner: str, repo: str, comment_id: Union[int, str], body: str
    ) -> Dict[str, Any]:
        """更新Issue评论。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            comment_id: 评论ID
            body: 评论内容

        Returns:
            更新后的评论详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "comment_id": comment_id, "body": body},
            ["owner", "repo", "comment_id", "body"],
        )
        data = {"body": body}
        return self._patch(f"/repos/{owner}/{repo}/issues/comments/{comment_id}", json=data)

    def delete_comment(
        self, owner: str, repo: str, comment_id: Union[int, str]
    ) -> None:
        """删除Issue评论。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            comment_id: 评论ID
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "comment_id": comment_id},
            ["owner", "repo", "comment_id"],
        )
        self._delete(f"/repos/{owner}/{repo}/issues/comments/{comment_id}")