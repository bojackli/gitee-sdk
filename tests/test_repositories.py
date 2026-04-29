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

    def test_list_branches(self, mock_client):
        repos = Repositories(mock_client)
        repos.list_branches("owner", "repo", page=2, per_page=20)
        mock_client._get.assert_called_with(
            "/repos/owner/repo/branches",
            params={"page": 2, "per_page": 20},
        )

    def test_get_branch(self, mock_client):
        repos = Repositories(mock_client)
        repos.get_branch("owner", "repo", "main")
        mock_client._get.assert_called_with("/repos/owner/repo/branches/main")

    def test_list_commits(self, mock_client):
        repos = Repositories(mock_client)
        repos.list_commits("owner", "repo", sha="main", path="README.md")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/commits",
            params={"sha": "main", "path": "README.md"},
        )

    def test_get_commit(self, mock_client):
        repos = Repositories(mock_client)
        repos.get_commit("owner", "repo", "abc123")
        mock_client._get.assert_called_with("/repos/owner/repo/commits/abc123")

    def test_list_collaborators(self, mock_client):
        repos = Repositories(mock_client)
        repos.list_collaborators("owner", "repo", page=1, per_page=10)
        mock_client._get.assert_called_with(
            "/repos/owner/repo/collaborators",
            params={"page": 1, "per_page": 10},
        )

    def test_add_collaborator(self, mock_client):
        repos = Repositories(mock_client)
        repos.add_collaborator("owner", "repo", "alice", permission="push")
        mock_client.request.assert_called_with(
            "PUT",
            "/repos/owner/repo/collaborators/alice",
            params=None,
            json={"permission": "push"},
            data=None,
        )

    def test_remove_collaborator(self, mock_client):
        repos = Repositories(mock_client)
        repos.remove_collaborator("owner", "repo", "alice")
        mock_client.request.assert_called_with(
            "DELETE",
            "/repos/owner/repo/collaborators/alice",
            params=None,
        )

    def test_create_fork(self, mock_client):
        repos = Repositories(mock_client)
        repos.create_fork("owner", "repo", organization="org", name="forked")
        mock_client._post.assert_called_with(
            "/repos/owner/repo/forks",
            json={"organization": "org", "name": "forked"},
        )

    def test_get_raw(self, mock_client):
        repos = Repositories(mock_client)
        repos.get_raw("owner", "repo", "README.md", ref="main")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/raw/README.md",
            params={"ref": "main"},
        )
