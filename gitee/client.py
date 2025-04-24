"""Gitee API客户端模块。

该模块提供了与Gitee API交互的主要客户端类。
"""

import logging
from typing import Any, Dict, List, Optional, Union

import requests

from gitee.auth import Auth
from gitee.config import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_USER_AGENT
from gitee.exceptions import APIError, GiteeException, RateLimitExceeded
from gitee.resources.activities import Activities
from gitee.resources.checks import Checks
from gitee.resources.emails import Emails
from gitee.resources.enterprises import Enterprises
from gitee.resources.gists import Gists
from gitee.resources.issues import Issues
from gitee.resources.labels import Labels
from gitee.resources.milestones import Milestones
from gitee.resources.misc import Miscellaneous
from gitee.resources.organizations import Organizations
from gitee.resources.pulls import PullRequests
from gitee.resources.repositories import Repositories
from gitee.resources.search import Search
from gitee.resources.users import Users
from gitee.resources.webhooks import Webhooks

logger = logging.getLogger(__name__)


class GiteeClient:
    """Gitee API客户端类。

    该类是SDK的主入口，负责初始化配置、认证和创建资源对象。

    Args:
        token: Gitee API访问令牌
        base_url: Gitee API基础URL
        timeout: 请求超时时间（秒）
        **kwargs: 其他传递给httpx.Client的参数

    Examples:
        >>> from gitee import GiteeClient
        >>> client = GiteeClient(token="your_access_token")
        >>> repos = client.repositories.list()
        >>> for repo in repos:
        ...     print(f"{repo['full_name']}: {repo['description']}")
    """

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        **kwargs: Any,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth = Auth(token) if token else None
        self.session = self._create_session(**kwargs)

        # 初始化各资源模块
        self.repositories = Repositories(self)
        self.issues = Issues(self)
        self.pulls = PullRequests(self)
        self.users = Users(self)
        self.organizations = Organizations(self)
        self.gists = Gists(self)
        self.enterprises = Enterprises(self)
        self.emails = Emails(self)
        self.labels = Labels(self)
        self.milestones = Milestones(self)
        self.webhooks = Webhooks(self)
        self.activities = Activities(self)
        self.checks = Checks(self)
        self.search = Search(self)
        self.misc = Miscellaneous(self)

    def _create_session(self, **kwargs: Any) -> requests.Session:
        """创建并配置HTTP会话。

        Args:
            **kwargs: 传递给requests.Session的参数

        Returns:
            配置好的requests.Session实例
        """
        headers = kwargs.pop("headers", {})
        headers.setdefault("User-Agent", DEFAULT_USER_AGENT)
        headers.setdefault("Accept", "application/json")
        headers.setdefault("Content-Type", "application/json")

        if self.auth:
            headers = self.auth.apply_auth(headers)

        session = requests.Session()
        session.headers.update(headers)
        return session

    def _get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Union[Dict[str, Any], List[Dict[str, Any]], str, None]:
        """发送GET请求。

        Args:
            url: 请求URL
            params: URL查询参数
            **kwargs: 其他传递给request方法的参数

        Returns:
            解析后的JSON响应
        """
        return self.request("GET", url, params=params, **kwargs)

    def _post(self, url: str, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Union[Dict[str, Any], List[Dict[str, Any]], str, None]:
        """发送POST请求。

        Args:
            url: 请求URL
            params: URL查询参数
            json: JSON数据
            data: 表单数据
            **kwargs: 其他传递给request方法的参数

        Returns:
            解析后的JSON响应
        """
        return self.request("POST", url, params=params, json=json, data=data, **kwargs)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], str, None]:
        """发送HTTP请求并处理响应。

        Args:
            method: HTTP方法（GET, POST, PUT, PATCH, DELETE）
            url: 请求URL，如果不是完整URL则会添加base_url前缀
            params: URL查询参数
            data: 表单数据
            json: JSON数据
            **kwargs: 其他传递给requests.Session.request的参数

        Returns:
            解析后的JSON响应，或者当响应不是有效JSON格式时返回原始字符串内容

        Raises:
            GiteeException: 请求过程中发生错误
            APIError: API返回错误
            RateLimitExceeded: 超出API速率限制
        """
        if not url.startswith("http"):
            url = f"{self.base_url}{url}"

        logger.debug(f"Sending {method} request to {url}")
        logger.debug(f"Request headers: {self.session.headers}")
        logger.debug(f"Request params: {params}")
        logger.debug(f"Request data: {data}")
        logger.debug(f"Request json: {json}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                timeout=self.timeout,
                **kwargs
            )
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response content: {response.text}")
            response.raise_for_status()

            # 检查速率限制
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining and int(remaining) == 0:
                reset_time = response.headers.get("X-RateLimit-Reset")
                raise RateLimitExceeded(reset_time)

            # 处理空响应
            if not response.content or response.status_code == 204:
                return None

            try:
                return response.json()
            except ValueError:
                # 处理非JSON响应
                logger.debug("Response is not a valid JSON, returning raw content")
                return response.text

        except requests.exceptions.HTTPError as e:
            response = e.response
            try:
                error_data = response.json()
                message = error_data.get("message", str(e))
                error_code = error_data.get("error_code", "unknown")
                raise APIError(response.status_code, error_code, message)
            except (ValueError, KeyError):
                raise APIError(response.status_code, "unknown", str(e))

        except requests.exceptions.RequestException as e:
            raise GiteeException(f"Request failed: {str(e)}")

    def close(self) -> None:
        """关闭HTTP会话。"""
        self.session.close()

    def __enter__(self) -> "GiteeClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()