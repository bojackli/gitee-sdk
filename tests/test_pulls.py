import pytest
from unittest.mock import Mock
from gitee.resources.pulls import PullRequests

class TestPullRequests:
    
    @pytest.fixture
    def mock_client(self):
        return Mock()
    
    def test_list_pulls(self, mock_client):
        """测试获取pull request列表"""
        pulls = PullRequests(mock_client)
        pulls.list("owner", "repo")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/pulls", 
            params={}
        )
    
    def test_list_pulls_with_params(self, mock_client):
        """测试带参数的pull request列表查询"""
        pulls = PullRequests(mock_client)
        pulls.list("owner", "repo", state="open", sort="created", direction="asc")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/pulls", 
            params={"state": "open", "sort": "created", "direction": "asc"}
        )
    
    def test_get_pull(self, mock_client):
        """测试获取单个pull request"""
        pulls = PullRequests(mock_client)
        pulls.get("owner", "repo", 123)
        mock_client._get.assert_called_with(
            "/repos/owner/repo/pulls/123"
        )
    
    def test_create_pull(self, mock_client):
        """测试创建pull request"""
        pulls = PullRequests(mock_client)
        pulls.create("owner", "repo", "title", "head", "base", "body")
        mock_client._post.assert_called_with(
            "/repos/owner/repo/pulls",
            json={"title": "title", "head": "head", "base": "base", "body": "body"}
        )