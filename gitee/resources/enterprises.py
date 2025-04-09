"""企业资源模块。

该模块提供了与Gitee企业相关的API功能。
"""

from typing import Any, Dict, List

from gitee.resources.base import Resource
from gitee.utils import validate_required_params


class Enterprises(Resource):
    """企业资源类。

    提供与Gitee企业相关的API功能。
    """

    def list(self) -> List[Dict[str, Any]]:
        """获取当前用户所属的企业列表。

        Returns:
            企业列表
        """
        return self._get("/enterprises")

    def get(self, enterprise: str) -> Dict[str, Any]:
        """获取企业信息。

        Args:
            enterprise: 企业路径

        Returns:
            企业信息
        """
        validate_required_params({"enterprise": enterprise}, ["enterprise"])
        return self._get(f"/enterprises/{enterprise}")

    def update(self, enterprise: str, **kwargs) -> Dict[str, Any]:
        """更新企业信息。

        Args:
            enterprise: 企业路径
            **kwargs: 其他可选参数

        Returns:
            更新后的企业信息
        """
        validate_required_params({"enterprise": enterprise}, ["enterprise"])
        return self._patch(f"/enterprises/{enterprise}", json=kwargs)