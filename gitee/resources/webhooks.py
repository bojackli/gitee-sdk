from .base import Resource

class Webhooks(Resource):
    """Webhooks相关API"""
    
    def list_webhooks(self, owner, repo, page=None, per_page=None):
        """获取仓库的webhook列表
        
        参数:
            owner: 仓库所属用户
            repo: 仓库名称
            page: 页码
            per_page: 每页数量
        """
        params = {}
        if page:
            params["page"] = page
        if per_page:
            params["per_page"] = per_page
            
        return self._get(f"/repos/{owner}/{repo}/hooks", params=params)
    
    def create_webhook(self, owner, repo, url, content_type="json", secret=None, events=None):
        """创建webhook
        
        参数:
            owner: 仓库所属用户
            repo: 仓库名称
            url: webhook的URL
            content_type: 内容类型(json或form)
            secret: 密钥
            events: 触发事件列表
        """
        data = {
            "url": url,
            "content_type": content_type
        }
        if secret:
            data["secret"] = secret
        if events:
            data["events"] = events
            
        return self._post(f"/repos/{owner}/{repo}/hooks", json=data)
    
    def get_webhook(self, owner, repo, id):
        """获取单个webhook
        
        参数:
            owner: 仓库所属用户
            repo: 仓库名称
            id: webhook的ID
        """
        return self._get(f"/repos/{owner}/{repo}/hooks/{id}")
    
    def update_webhook(self, owner, repo, id, url=None, content_type=None, secret=None, events=None):
        """更新webhook
        
        参数:
            owner: 仓库所属用户
            repo: 仓库名称
            id: webhook的ID
            url: webhook的URL
            content_type: 内容类型(json或form)
            secret: 密钥
            events: 触发事件列表
        """
        data = {}
        if url:
            data["url"] = url
        if content_type:
            data["content_type"] = content_type
        if secret:
            data["secret"] = secret
        if events:
            data["events"] = events
            
        return self._patch(f"/repos/{owner}/{repo}/hooks/{id}", json=data)
    
    def delete_webhook(self, owner, repo, id):
        """删除webhook
        
        参数:
            owner: 仓库所属用户
            repo: 仓库名称
            id: webhook的ID
        """
        return self._delete(f"/repos/{owner}/{repo}/hooks/{id}")
    
    def test_webhook(self, owner, repo, id):
        """测试webhook
        
        参数:
            owner: 仓库所属用户
            repo: 仓库名称
            id: webhook的ID
        """
        return self._post(f"/repos/{owner}/{repo}/hooks/{id}/tests")