from .base import Resource

class Search(Resource):
    """仓库搜索相关API"""
    
    def search(self, q, sort=None, order=None, page=None, per_page=None, **kwargs):
        """
        搜索仓库
        
        参数:
            q: 搜索关键词
            sort: 排序字段(可选: stars, forks, updated)
            order: 排序方式(可选: asc, desc)
            page: 页码
            per_page: 每页数量
            **kwargs: 其他可选参数
        
        返回:
            分页的搜索结果
        """
        params = {"q": q}
        if sort:
            params["sort"] = sort
        if order:
            params["order"] = order
        if page:
            params["page"] = page
        if per_page:
            params["per_page"] = per_page
        params.update(kwargs)
        
        return self._get("/search/repositories", params=params)