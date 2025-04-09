"""用户资源模块。

该模块提供了与Gitee用户相关的API功能。
"""

from typing import Any, Dict, List, Optional, Union

from gitee.resources.base import PaginatedList, Resource
from gitee.utils import filter_none_values, validate_required_params


class Users(Resource):
    """用户资源类。

    提供与Gitee用户相关的API功能。
    """

    def get(self, username: Optional[str] = None) -> Dict[str, Any]:
        """获取用户信息。

        如果不指定username，则获取当前认证用户的信息。

        Args:
            username: 用户名

        Returns:
            用户信息
        """
        if username:
            return self._get(f"/users/{username}")
        return self._get("/user")

    def update(self, **kwargs: Any) -> Dict[str, Any]:
        """更新当前认证用户的信息。

        Args:
            **kwargs: 用户信息字段，可包含name, email, blog, company, location, bio等

        Returns:
            更新后的用户信息
        """
        data = filter_none_values(kwargs)
        return self._patch("/user", json=data)

    def list_followers(
        self,
        username: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取用户的关注者列表。

        如果不指定username，则获取当前认证用户的关注者列表。

        Args:
            username: 用户名
            page: 页码
            per_page: 每页数量

        Returns:
            关注者列表
        """
        params = filter_none_values({"page": page, "per_page": per_page})
        if username:
            return self._get(f"/users/{username}/followers", params=params)
        return self._get("/user/followers", params=params)

    def list_following(
        self,
        username: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取用户关注的用户列表。

        如果不指定username，则获取当前认证用户关注的用户列表。

        Args:
            username: 用户名
            page: 页码
            per_page: 每页数量

        Returns:
            关注的用户列表
        """
        params = filter_none_values({"page": page, "per_page": per_page})
        if username:
            return self._get(f"/users/{username}/following", params=params)
        return self._get("/user/following", params=params)

    def is_following(self, username: str) -> bool:
        """检查当前认证用户是否关注了指定用户。

        Args:
            username: 用户名

        Returns:
            是否关注
        """
        validate_required_params({"username": username}, ["username"])
        try:
            self._get(f"/user/following/{username}")
            return True
        except Exception:
            return False

    def follow(self, username: str) -> None:
        """关注指定用户。

        Args:
            username: 用户名
        """
        validate_required_params({"username": username}, ["username"])
        self._put(f"/user/following/{username}")

    def unfollow(self, username: str) -> None:
        """取消关注指定用户。

        Args:
            username: 用户名
        """
        validate_required_params({"username": username}, ["username"])
        self._delete(f"/user/following/{username}")

    def list_keys(
        self, page: Optional[int] = None, per_page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """获取当前认证用户的SSH密钥列表。

        Args:
            page: 页码
            per_page: 每页数量

        Returns:
            SSH密钥列表
        """
        params = filter_none_values({"page": page, "per_page": per_page})
        return self._get("/user/keys", params=params)

    def get_key(self, key_id: Union[int, str]) -> Dict[str, Any]:
        """获取当前认证用户的SSH密钥详情。

        Args:
            key_id: 密钥ID

        Returns:
            SSH密钥详情
        """
        validate_required_params({"key_id": key_id}, ["key_id"])
        return self._get(f"/user/keys/{key_id}")

    def create_key(self, title: str, key: str) -> Dict[str, Any]:
        """为当前认证用户添加SSH密钥。

        Args:
            title: 密钥标题
            key: 密钥内容

        Returns:
            创建的SSH密钥详情
        """
        validate_required_params({"title": title, "key": key}, ["title", "key"])
        data = {"title": title, "key": key}
        return self._post("/user/keys", json=data)

    def delete_key(self, key_id: Union[int, str]) -> None:
        """删除当前认证用户的SSH密钥。

        Args:
            key_id: 密钥ID
        """
        validate_required_params({"key_id": key_id}, ["key_id"])
        self._delete(f"/user/keys/{key_id}")

    def list_repos(
        self,
        username: Optional[str] = None,
        type: Optional[str] = None,
        sort: Optional[str] = None,
        direction: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取用户的仓库列表。

        如果不指定username，则获取当前认证用户的仓库列表。

        Args:
            username: 用户名
            type: 仓库类型，可选值：all, owner, member
            sort: 排序字段，可选值：created, updated, pushed, full_name
            direction: 排序方向，可选值：asc, desc
            page: 页码
            per_page: 每页数量

        Returns:
            仓库列表
        """
        params = filter_none_values(
            {
                "type": type,
                "sort": sort,
                "direction": direction,
                "page": page,
                "per_page": per_page,
            }
        )
        if username:
            return self._get(f"/users/{username}/repos", params=params)
        return self._get("/user/repos", params=params)