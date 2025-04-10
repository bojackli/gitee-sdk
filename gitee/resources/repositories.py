"""仓库资源模块。

该模块提供了与Gitee仓库相关的API功能。
"""

from typing import Any, Dict, List, Optional, Union

from gitee.resources.base import PaginatedList, Resource
from gitee.utils import filter_none_values, validate_required_params


class Repositories(Resource):
    """仓库资源类。

    提供与Gitee仓库相关的API功能。
    """

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

    def get(
        self, owner: str, repo: str
    ) -> Dict[str, Any]:
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
            license_template: 许可证模板，具体格式要求请参考Gitee API文档：https://gitee.com/api/v5/swagger#/postV5UserRepos
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
        self, owner: str, repo: str, page: Optional[int] = None, per_page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取仓库分支列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            page: 页码
            per_page: 每页数量

        Returns:
            分支列表
        """
        validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
        params = filter_none_values({"page": page, "per_page": per_page})
        return self._get(f"/repos/{owner}/{repo}/branches", params=params)

    def get_branch(
        self, owner: str, repo: str, branch: str
    ) -> Dict[str, Any]:
        """获取仓库分支详情。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            branch: 分支名称

        Returns:
            分支详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "branch": branch},
            ["owner", "repo", "branch"],
        )
        return self._get(f"/repos/{owner}/{repo}/branches/{branch}")

    def list_collaborators(
        self,
        owner: str,
        repo: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库协作者列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            page: 页码
            per_page: 每页数量

        Returns:
            协作者列表
        """
        validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
        params = filter_none_values({"page": page, "per_page": per_page})
        return self._get(f"/repos/{owner}/{repo}/collaborators", params=params)

    def add_collaborator(
        self, owner: str, repo: str, username: str, permission: Optional[str] = None
    ) -> None:
        """添加仓库协作者。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            username: 用户名
            permission: 权限，可选值：pull, push, admin
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "username": username},
            ["owner", "repo", "username"],
        )
        data = filter_none_values({"permission": permission})
        self._put(f"/repos/{owner}/{repo}/collaborators/{username}", json=data)

    def remove_collaborator(self, owner: str, repo: str, username: str) -> None:
        """移除仓库协作者。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            username: 用户名
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "username": username},
            ["owner", "repo", "username"],
        )
        self._delete(f"/repos/{owner}/{repo}/collaborators/{username}")

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
        """获取仓库提交列表。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sha: 分支名称、标签名称或提交SHA
            path: 文件路径
            author: 作者
            since: 起始时间，ISO 8601格式
            until: 结束时间，ISO 8601格式
            page: 页码
            per_page: 每页数量

        Returns:
            提交列表
        """
        validate_required_params({"owner": owner, "repo": repo}, ["owner", "repo"])
        params = filter_none_values(
            {
                "sha": sha,
                "path": path,
                "author": author,
                "since": since,
                "until": until,
                "page": page,
                "per_page": per_page,
            }
        )
        return self._get(f"/repos/{owner}/{repo}/commits", params=params)

    def get_commit(
        self, owner: str, repo: str, sha: str
    ) -> Dict[str, Any]:
        """获取仓库提交详情。

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sha: 提交SHA

        Returns:
            提交详情
        """
        validate_required_params(
            {"owner": owner, "repo": repo, "sha": sha}, ["owner", "repo", "sha"]
        )
        return self._get(f"/repos/{owner}/{repo}/commits/{sha}")

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
        self, owner: str, repo: str, organization: Optional[str] = None, name: Optional[str] = None
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
        validate_required_params({"owner": owner, "repo": repo, "path": path}, ["owner", "repo", "path"])
        params = filter_none_values({"ref": ref})
        return self._get(f"/repos/{owner}/{repo}/raw/{path}", params=params)