"""仓库资源模块。

该模块提供了与Gitee仓库相关的API功能。
"""

from typing import Any, Dict, List, Optional, Union

from gitee.resources.base import PaginatedList, Resource
from gitee.resources.branches import Branches
from gitee.resources.collaborators import Collaborators
from gitee.resources.commits import Commits
from gitee.utils import filter_none_values, validate_required_params


class Repositories(Resource):
    """仓库资源类。

    提供与Gitee仓库相关的API功能。
    """

    def __init__(self, client: Any) -> None:
        super().__init__(client)
        self._branches = Branches(client)
        self._commits = Commits(client)
        self._collaborators = Collaborators(client)

    def list(
        self,
        owner: str,
        type: Optional[str] = None,
        sort: Optional[str] = None,
        direction: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """获取仓库列表。

        Args:
            owner: 仓库所有者
            type: 仓库类型，可选值：all, owner, public, private, member
            sort: 排序字段，可选值：created, updated, pushed, full_name
            direction: 排序方向，可选值：asc, desc
            page: 页码
            per_page: 每页数量
            **kwargs: 其他参数

        Returns:
            仓库列表
        """
        validate_required_params({"owner": owner}, ["owner"])
        params = filter_none_values(
            {
                "type": type,
                "sort": sort,
                "direction": direction,
                "page": page,
                "per_page": per_page,
                **kwargs,
            }
        )
        return self._get(f"/users/{owner}/repos", params=params)

    def get(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库详情。

        Args:
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            仓库详情
        """
        validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
        return self._get(f"/repos/{owner}/{repo}")

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        private: Optional[bool] = None,
        homepage: Optional[str] = None,
        has_issues: Optional[bool] = None,
        has_wiki: Optional[bool] = None,
        auto_init: Optional[bool] = None,
        gitignore_template: Optional[str] = None,
        license_template: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """创建仓库。

        Args:
            name: 仓库名称 (必填)
            description: 仓库描述
            private: 是否私有 (True/False)
            homepage: 主页URL
            has_issues: 是否启用Issues (True/False)
            has_wiki: 是否启用Wiki (True/False)
            auto_init: 是否自动初始化 (True/False)
            gitignore_template: .gitignore模板
            license_template: 许可证模板，具体格式要求请参考Gitee API文档
            **kwargs: 其他参数

        Returns:
            创建的仓库详情

        API文档参考: https://gitee.com/api/v5/swagger#/postV5UserRepos
        """
        validate_required_params({"name": name}, ["name"])
        data = filter_none_values(
            {
                "name": name,
                "description": description,
                "private": private,
                "homepage": homepage,
                "has_issues": has_issues,
                "has_wiki": has_wiki,
                "auto_init": auto_init,
                "gitignore_template": gitignore_template,
                "license_template": license_template,
                **kwargs,
            }
        )
        return self._post("/user/repos", json=data)

    def update(
        self,
        owner: str,
        repo: str,
        name: str,
        description: Optional[str] = None,
        homepage: Optional[str] = None,
        private: Optional[bool] = None,
        has_issues: Optional[bool] = None,
        has_wiki: Optional[bool] = None,
        default_branch: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """更新仓库。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            name: 新的仓库名称
            description: 仓库描述
            homepage: 主页URL
            private: 是否私有 (True/False)
            has_issues: 是否启用Issues (True/False)
            has_wiki: 是否启用Wiki (True/False)
            default_branch: 默认分支
            **kwargs: 其他参数

        Returns:
            更新后的仓库详情

        API文档参考: https://gitee.com/api/v5/swagger#/patchV5ReposOwnerRepo
        """
        validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
        data = filter_none_values(
            {
                "name": name,
                "description": description,
                "homepage": homepage,
                "private": private,
                "has_issues": has_issues,
                "has_wiki": has_wiki,
                "default_branch": default_branch,
                **kwargs,
            }
        )
        return self._patch(f"/repos/{owner}/{repo}", json=data)

    def delete(self, owner: str, repo: str) -> None:
        """删除仓库。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
        """
        validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
        self._delete(f"/repos/{owner}/{repo}")

    def list_branches(
        self,
        owner: str,
        repo: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库分支列表。"""
        return self._branches.list(owner, repo, page=page, per_page=per_page)

    def get_branch(self, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        """获取仓库分支详情。"""
        return self._branches.get(owner, repo, branch)

    def list_branches_paginated(
        self,
        owner: str,
        repo: str,
        per_page: Optional[int] = None,
    ) -> PaginatedList:
        """获取可迭代分页仓库分支列表。"""
        return self._branches.list_paginated(owner, repo, per_page=per_page)

    def list_collaborators(
        self,
        owner: str,
        repo: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库协作者列表。"""
        return self._collaborators.list(owner, repo, page=page, per_page=per_page)

    def add_collaborator(
        self,
        owner: str,
        repo: str,
        username: str,
        permission: Optional[str] = None,
    ) -> None:
        """添加仓库协作者。"""
        self._collaborators.add(owner, repo, username, permission=permission)

    def remove_collaborator(self, owner: str, repo: str, username: str) -> None:
        """移除仓库协作者。"""
        self._collaborators.remove(owner, repo, username)

    def list_commits(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        author: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库提交列表。"""
        return self._commits.list(
            owner,
            repo,
            sha=sha,
            path=path,
            author=author,
            since=since,
            until=until,
            page=page,
            per_page=per_page,
        )

    def get_commit(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """获取仓库提交详情。"""
        return self._commits.get(owner, repo, sha)

    def list_commits_paginated(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        author: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        per_page: Optional[int] = None,
    ) -> PaginatedList:
        """获取可迭代分页仓库提交列表。"""
        return self._commits.list_paginated(
            owner,
            repo,
            sha=sha,
            path=path,
            author=author,
            since=since,
            until=until,
            per_page=per_page,
        )

    def list_forks(
        self,
        owner: str,
        repo: str,
        sort: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库Fork列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sort: 排序字段，可选值：newest, oldest, stargazers
            page: 页码
            per_page: 每页数量

        Returns:
            Fork列表
        """
        validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
        params = filter_none_values({"sort": sort, "page": page, "per_page": per_page})
        return self._get(f"/repos/{owner}/{repo}/forks", params=params)

    def create_fork(
        self,
        owner: str,
        repo: str,
        organization: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """创建仓库Fork。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            organization: 组织名称
            name: fork后的仓库名称

        Returns:
            Fork详情
        """
        validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
        data = filter_none_values({"organization": organization, "name": name})
        return self._post(f"/repos/{owner}/{repo}/forks", json=data)

    def get_raw(
        self, owner: str, repo: str, path: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取仓库原始文件内容。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            path: 文件路径
            ref: 分支/标签/提交SHA，默认为默认分支

        Returns:
            文件原始内容
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "path": path}, ["owner", "repo", "path"]
        )
        params = filter_none_values({"ref": ref})
        return self._get(f"/repos/{owner}/{repo}/raw/{path}", params=params)
