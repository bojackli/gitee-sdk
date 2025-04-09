"""组织资源模块。

该模块提供了Gitee API的组织相关功能。
"""

from typing import Any, Dict, List, Optional

from gitee.resources.base import Resource


class Organizations(Resource):
    """组织资源类。

    提供Gitee API的组织相关功能，如获取组织列表、创建组织、更新组织信息等。
    """

    def list_organizations(self) -> List[Dict[str, Any]]:
        """获取授权用户的组织列表。

        Returns:
            组织列表信息
        """
        return self._get("/user/orgs")

    def get_organization(self, org: str) -> Dict[str, Any]:
        """获取指定组织信息。

        Args:
            org: 组织的路径(path/login)

        Returns:
            组织信息
        """
        return self._get(f"/orgs/{org}")

    def update_organization(self, org: str, **kwargs) -> Dict[str, Any]:
        """更新组织信息。

        Args:
            org: 组织的路径(path/login)
            **kwargs: 其他可选参数，如name、description、location等

        Returns:
            更新后的组织信息
        """
        return self._patch(f"/orgs/{org}", data=kwargs)

    def list_organization_members(self, org: str) -> List[Dict[str, Any]]:
        """获取组织成员列表。

        Args:
            org: 组织的路径(path/login)

        Returns:
            组织成员列表
        """
        return self._get(f"/orgs/{org}/members")