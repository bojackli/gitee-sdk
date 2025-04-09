import pytest
from unittest.mock import Mock
from gitee.resources.issues import Issues

class TestIssues:
    
    @pytest.fixture
    def mock_client(self):
        return Mock()
    
    def test_list_issues(self, mock_client):
        """测试获取issue列表"""
        issues = Issues(mock_client)
        issues.list("owner", "repo")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/issues", 
            params={}
        )
    
    def test_list_issues_with_params(self, mock_client):
        """测试带参数的issue列表查询"""
        issues = Issues(mock_client)
        issues.list("owner", "repo", state="open", sort="created", direction="asc")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/issues", 
            params={"state": "open", "sort": "created", "direction": "asc"}
        )
    
    def test_get_issue(self, mock_client):
        """测试获取单个issue"""
        issues = Issues(mock_client)
        issues.get("owner", "repo", 123)
        mock_client._get.assert_called_with(
            "/repos/owner/repo/issues/123"
        )
    
    def test_create_issue(self, mock_client):
        """测试创建issue"""
        issues = Issues(mock_client)
        issues.create("owner", "repo", "title", "body")
        mock_client._post.assert_called_with(
            "/repos/owner/repo/issues",
            json={"title": "title", "body": "body"}
        )