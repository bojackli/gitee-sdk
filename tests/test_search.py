import pytest
from unittest.mock import Mock
from gitee.resources.search import Search

class TestSearch:
    
    @pytest.fixture
    def mock_client(self):
        return Mock()
    
    def test_basic_search(self, mock_client):
        """测试基本搜索功能"""
        search = Search(mock_client)
        search.search("python")
        mock_client._get.assert_called_with(
            "/search/repositories", 
            params={"q": "python"}
        )
    
    def test_search_with_sort(self, mock_client):
        """测试带排序参数的搜索"""
        search = Search(mock_client)
        search.search("python", sort="stars", order="desc")
        mock_client._get.assert_called_with(
            "/search/repositories", 
            params={"q": "python", "sort": "stars", "order": "desc"}
        )
    
    def test_search_with_pagination(self, mock_client):
        """测试带分页参数的搜索"""
        search = Search(mock_client)
        search.search("python", page=2, per_page=20)
        mock_client._get.assert_called_with(
            "/search/repositories", 
            params={"q": "python", "page": 2, "per_page": 20}
        )
    
    def test_search_with_additional_params(self, mock_client):
        """测试带额外参数的搜索"""
        search = Search(mock_client)
        search.search("python", language="Python", license="MIT")
        mock_client._get.assert_called_with(
            "/search/repositories", 
            params={"q": "python", "language": "Python", "license": "MIT"}
        )