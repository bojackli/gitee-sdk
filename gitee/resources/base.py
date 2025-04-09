"""资源基础模块。

该模块提供了所有资源模块的基类。
"""

from typing import Any, Dict, List, Optional, Union

from gitee.config import DEFAULT_PAGE_SIZE


class Resource:
    """资源基类。

    所有资源模块的基类，提供通用的请求方法。

    Args:
        client: GiteeClient实例
    """

    def __init__(self, client: Any) -> None:
        self.client = client

    def _get(
        self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """发送GET请求。

        Args:
            url: 请求URL
            params: URL查询参数
            **kwargs: 其他传递给client._get的参数

        Returns:
            解析后的JSON响应
        """
        if params is None and not kwargs:
            return self.client._get(url)
        return self.client._get(url, params=params, **kwargs)

    def _post(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """发送POST请求。

        Args:
            url: 请求URL
            params: URL查询参数
            json: JSON数据
            data: 表单数据
            **kwargs: 其他传递给client.request的参数

        Returns:
            解析后的JSON响应
        """
        request_kwargs = {}
        if params is not None:
            request_kwargs['params'] = params
        if json is not None:
            request_kwargs['json'] = json
        if data is not None:
            request_kwargs['data'] = data
        request_kwargs.update(kwargs)
        return self.client._post(url, **request_kwargs)

    def _put(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """发送PUT请求。

        Args:
            url: 请求URL
            params: URL查询参数
            json: JSON数据
            data: 表单数据
            **kwargs: 其他传递给client.request的参数

        Returns:
            解析后的JSON响应
        """
        return self.client.request(
            "PUT", url, params=params, json=json, data=data, **kwargs
        )

    def _patch(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """发送PATCH请求。

        Args:
            url: 请求URL
            params: URL查询参数
            json: JSON数据
            data: 表单数据
            **kwargs: 其他传递给client.request的参数

        Returns:
            解析后的JSON响应
        """
        return self.client.request(
            "PATCH", url, params=params, json=json, data=data, **kwargs
        )

    def _delete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """发送DELETE请求。

        Args:
            url: 请求URL
            params: URL查询参数
            **kwargs: 其他传递给client.request的参数

        Returns:
            解析后的JSON响应
        """
        return self.client.request("DELETE", url, params=params, **kwargs)


class PaginatedList:
    """分页列表类。

    处理Gitee API返回的分页数据。

    Args:
        client: GiteeClient实例
        url: 请求URL
        params: URL查询参数
        item_key: 响应中包含列表项的键，默认为None（表示响应本身就是列表）
    """

    def __init__(
        self,
        client: Any,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        item_key: Optional[str] = None,
    ) -> None:
        self.client = client
        self.url = url
        self.params = params or {}
        self.item_key = item_key
        self.current_page = 1
        self.per_page = DEFAULT_PAGE_SIZE
        self.total_pages = None
        self.total_count = None
        self.items = []

    def get_page(
        self, page: int = 1, per_page: int = DEFAULT_PAGE_SIZE
    ) -> List[Dict[str, Any]]:
        """获取指定页的数据。

        Args:
            page: 页码
            per_page: 每页项数

        Returns:
            当前页的数据列表
        """
        params = self.params.copy()
        params.update({"page": page, "per_page": per_page})

        response = self.client.request("GET", self.url, params=params)

        # 更新分页信息
        self.current_page = page
        self.per_page = per_page

        # 处理响应
        if self.item_key and isinstance(response, dict):
            items = response.get(self.item_key, [])
        else:
            items = response if isinstance(response, list) else []

        return items

    def __iter__(self) -> "PaginatedList":
        self.current_page = 1
        self.items = self.get_page(self.current_page, self.per_page)
        self._index = 0
        return self

    def __next__(self) -> Dict[str, Any]:
        if self._index >= len(self.items):
            self.current_page += 1
            self.items = self.get_page(self.current_page, self.per_page)
            self._index = 0
            if not self.items:
                raise StopIteration

        item = self.items[self._index]
        self._index += 1
        return item

    def all(self) -> List[Dict[str, Any]]:
        """获取所有页的数据。

        Returns:
            所有页的数据列表
        """
        result = []
        for item in self:
            result.append(item)
        return result