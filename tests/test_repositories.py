import pytest
from unittest.mock import Mock
from gitee.resources.repositories import Repositories

class TestRepositories:
    
    @pytest.fixture
    def mock_client(self):
        return Mock()
    
    def test_get_repo(self, mock_client):
        """测试获取仓库信息"""
        repos = Repositories(mock_client)
        repos.get("owner", "repo")
        mock_client._get.assert_called_with(
            "/repos/owner/repo"
        )
    
    def test_list_repos(self, mock_client):
        """测试获取用户仓库列表"""
        repos = Repositories(mock_client)
        repos.list("owner")
        mock_client._get.assert_called_with(
            "/users/owner/repos", 
            params={}
        )
    
    def test_list_repos_with_params(self, mock_client):
        """测试带参数的仓库列表查询"""
        repos = Repositories(mock_client)
        repos.list("owner", type="owner", sort="updated", direction="desc")
        mock_client._get.assert_called_with(
            "/users/owner/repos", 
            params={"type": "owner", "sort": "updated", "direction": "desc"}
        )
    
    def test_create_repo(self, mock_client):
        """测试创建仓库"""
        repos = Repositories(mock_client)
        repos.create("repo_name", "description", "private")
        mock_client._post.assert_called_with(
            "/user/repos",
            json={"name": "repo_name", "description": "description", "private": "private"}
        )