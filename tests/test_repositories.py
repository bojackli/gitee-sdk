from unittest.mock import Mock

import pytest

from gitee.resources.repositories import Repositories


class TestRepositories:

    @pytest.fixture
    def mock_client(self):
        return Mock()

    def test_get_repo(self, mock_client):
        """测试获取仓库信息"""
        repos = Repositories(mock_client)
        repos.get("owner", "repo")
        mock_client._get.assert_called_with("/repos/owner/repo")

    def test_list_repos(self, mock_client):
        """测试获取用户仓库列表"""
        repos = Repositories(mock_client)
        repos.list("owner")
        mock_client._get.assert_called_with("/users/owner/repos", params={})

    def test_list_repos_with_params(self, mock_client):
        """测试带参数的仓库列表查询"""
        repos = Repositories(mock_client)
        repos.list("owner", type="owner", sort="updated", direction="desc")
        mock_client._get.assert_called_with(
            "/users/owner/repos",
            params={"type": "owner", "sort": "updated", "direction": "desc"},
        )

    def test_list_repos_paginated(self, mock_client):
        repos = Repositories(mock_client)
        paginated = repos.list_paginated("owner", type="owner", per_page=20)
        assert paginated.client is mock_client
        assert paginated.url == "/users/owner/repos"
        assert paginated.params == {"type": "owner", "per_page": 20}

    def test_list_branches_paginated(self, mock_client):
        repos = Repositories(mock_client)
        paginated = repos.list_branches_paginated("owner", "repo", per_page=20)
        assert paginated.client is mock_client
        assert paginated.url == "/repos/owner/repo/branches"
        assert paginated.params == {"per_page": 20}

    def test_list_commits_paginated(self, mock_client):
        repos = Repositories(mock_client)
        paginated = repos.list_commits_paginated("owner", "repo", sha="main")
        assert paginated.client is mock_client
        assert paginated.url == "/repos/owner/repo/commits"
        assert paginated.params == {"sha": "main"}

    def test_create_repo(self, mock_client):
        """测试创建仓库"""
        repos = Repositories(mock_client)
        repos.create("repo_name", "description", "private")
        mock_client._post.assert_called_with(
            "/user/repos",
            json={
                "name": "repo_name",
                "description": "description",
                "private": "private",
            },
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

    def test_get_readme(self, mock_client):
        repos = Repositories(mock_client)
        repos.get_readme("owner", "repo", ref="main")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/readme",
            params={"ref": "main"},
        )

    def test_get_contents_defaults_to_root(self, mock_client):
        repos = Repositories(mock_client)
        repos.get_contents("owner", "repo")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/contents",
            params={},
        )

    def test_get_contents_with_path_and_ref(self, mock_client):
        repos = Repositories(mock_client)
        repos.get_contents("owner", "repo", "src/app.py", ref="main")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/contents/src/app.py",
            params={"ref": "main"},
        )

    def test_create_file(self, mock_client):
        repos = Repositories(mock_client)
        repos.create_file(
            "owner",
            "repo",
            "README.md",
            content="hello",
            message="add readme",
            branch="main",
            committer_name="Alice",
        )
        mock_client._post.assert_called_with(
            "/repos/owner/repo/contents/README.md",
            json={
                "content": "hello",
                "message": "add readme",
                "branch": "main",
                "committer_name": "Alice",
            },
        )

    def test_update_file(self, mock_client):
        repos = Repositories(mock_client)
        repos.update_file(
            "owner",
            "repo",
            "README.md",
            content="hello again",
            message="update readme",
            sha="abc123",
        )
        mock_client.request.assert_called_with(
            "PUT",
            "/repos/owner/repo/contents/README.md",
            params=None,
            json={
                "content": "hello again",
                "message": "update readme",
                "sha": "abc123",
            },
            data=None,
        )

    def test_delete_file(self, mock_client):
        repos = Repositories(mock_client)
        repos.delete_file(
            "owner",
            "repo",
            "README.md",
            message="delete readme",
            sha="abc123",
            branch="main",
        )
        mock_client.request.assert_called_with(
            "DELETE",
            "/repos/owner/repo/contents/README.md",
            params=None,
            json={"message": "delete readme", "sha": "abc123", "branch": "main"},
        )

    def test_create_commit(self, mock_client):
        repos = Repositories(mock_client)
        files = [{"path": "a.txt", "content": "A"}]
        repos.create_commit("owner", "repo", files=files, message="batch", branch="main")
        mock_client._post.assert_called_with(
            "/repos/owner/repo/commits",
            json={"files": files, "message": "batch", "branch": "main"},
        )

    def test_compare_commits(self, mock_client):
        repos = Repositories(mock_client)
        repos.compare_commits("owner", "repo", "main", "feature")
        mock_client._get.assert_called_with("/repos/owner/repo/compare/main...feature")

    def test_get_blame(self, mock_client):
        repos = Repositories(mock_client)
        repos.get_blame("owner", "repo", "README.md", ref="main")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/blame/README.md",
            params={"ref": "main"},
        )
