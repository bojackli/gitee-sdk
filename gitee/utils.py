"""工具模块。

该模块提供了一些辅助功能，如URL构建、参数验证等。
"""

from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

from gitee.exceptions import ValidationError


def validate_required_params(params: Dict[str, Any], required: List[str]) -> None:
    """验证必需参数。

    Args:
        params: 参数字典
        required: 必需参数列表

    Raises:
        ValidationError: 缺少必需参数时抛出
    """
    missing = [param for param in required if param not in params or params[param] is None]
    if missing:
        raise ValidationError(f"Missing required parameters: {', '.join(missing)}")


def build_url(base_url: str, path: str) -> str:
    """构建完整URL。

    Args:
        base_url: 基础URL
        path: 路径

    Returns:
        完整URL
    """
    # 确保base_url以/结尾，path不以/开头
    base_url = base_url.rstrip("/") + "/"
    path = path.lstrip("/")
    return urljoin(base_url, path)


def is_valid_url(url: str) -> bool:
    """检查URL是否有效。

    Args:
        url: 要检查的URL

    Returns:
        URL是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """过滤字典中的None值。

    Args:
        data: 原始字典

    Returns:
        过滤后的字典
    """
    return {k: v for k, v in data.items() if v is not None}


def format_path_params(path: str, **params: Any) -> str:
    """格式化路径参数。

    Args:
        path: 路径模板，如"/repos/{owner}/{repo}"
        **params: 路径参数

    Returns:
        格式化后的路径

    Raises:
        ValidationError: 缺少必需的路径参数时抛出
    """
    try:
        return path.format(**params)
    except KeyError as e:
        raise ValidationError(f"Missing required path parameter: {e}")