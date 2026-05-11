from unittest.mock import Mock

import pytest

from gitee.resources.pulls import PullRequests


class TestPullRequests:

    @pytest.fixture
    def mock_client(self):
        return Mock()

    def test_list_pulls(self, mock_client):
        """测试获取pull request列表"""
        pulls = PullRequests(mock_client)
        pulls.list("owner", "repo")
        mock_client._get.assert_called_with("/repos/owner/repo/pulls", params={})

    def test_list_pulls_with_params(self, mock_client):
        """测试带参数的pull request列表查询"""
        pulls = PullRequests(mock_client)
        pulls.list("owner", "repo", state="open", sort="created", direction="asc")
        mock_client._get.assert_called_with(
            "/repos/owner/repo/pulls",
            params={"state": "open", "sort": "created", "direction": "asc"},
        )

    def test_get_pull(self, mock_client):
        """测试获取单个pull request"""
        pulls = PullRequests(mock_client)
        pulls.get("owner", "repo", 123)
        mock_client._get.assert_called_with("/repos/owner/repo/pulls/123")

    def test_create_pull(self, mock_client):
        """测试创建pull request"""
        pulls = PullRequests(mock_client)
        pulls.create("owner", "repo", "title", "head", "base", "body")
        mock_client._post.assert_called_with(
            "/repos/owner/repo/pulls",
            json={"title": "title", "head": "head", "base": "base", "body": "body"},
        )

    def test_is_merged(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.is_merged("owner", "repo", 1)
        mock_client._get.assert_called_with("/repos/owner/repo/pulls/1/merge")

    def test_review_pull_request(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.review("owner", "repo", 1, event="APPROVE", body="ok")
        mock_client._post.assert_called_with(
            "/repos/owner/repo/pulls/1/review",
            json={"event": "APPROVE", "body": "ok"},
        )

    def test_test_pull_request(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.test("owner", "repo", 1, event="PASS", body="verified")
        mock_client._post.assert_called_with(
            "/repos/owner/repo/pulls/1/test",
            json={"event": "PASS", "body": "verified"},
        )

    def test_assign_reviewers(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.assign_reviewers("owner", "repo", 1, ["alice", "bob"])
        mock_client._post.assert_called_with(
            "/repos/owner/repo/pulls/1/assignees",
            json={"assignees": ["alice", "bob"]},
        )

    def test_unassign_reviewers(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.unassign_reviewers("owner", "repo", 1, ["alice"])
        mock_client.request.assert_called_with(
            "DELETE",
            "/repos/owner/repo/pulls/1/assignees",
            params=None,
            json={"assignees": ["alice"]},
        )

    def test_reset_reviewer_state(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.reset_reviewer_state("owner", "repo", 1, ["alice"])
        mock_client.request.assert_called_with(
            "PATCH",
            "/repos/owner/repo/pulls/1/assignees",
            params=None,
            json={"assignees": ["alice"]},
            data=None,
        )

    def test_assign_testers(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.assign_testers("owner", "repo", 1, ["alice"])
        mock_client._post.assert_called_with(
            "/repos/owner/repo/pulls/1/testers",
            json={"testers": ["alice"]},
        )

    def test_unassign_testers(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.unassign_testers("owner", "repo", 1, ["alice"])
        mock_client.request.assert_called_with(
            "DELETE",
            "/repos/owner/repo/pulls/1/testers",
            params=None,
            json={"testers": ["alice"]},
        )

    def test_reset_tester_state(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.reset_tester_state("owner", "repo", 1, ["alice"])
        mock_client.request.assert_called_with(
            "PATCH",
            "/repos/owner/repo/pulls/1/testers",
            params=None,
            json={"testers": ["alice"]},
            data=None,
        )

    def test_list_pull_request_issues(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.list_issues("owner", "repo", 1)
        mock_client._get.assert_called_with("/repos/owner/repo/pulls/1/issues")

    def test_list_pull_request_labels(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.list_labels("owner", "repo", 1)
        mock_client._get.assert_called_with("/repos/owner/repo/pulls/1/labels")

    def test_add_pull_request_labels(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.add_labels("owner", "repo", 1, ["bug"])
        mock_client._post.assert_called_with(
            "/repos/owner/repo/pulls/1/labels",
            json={"labels": ["bug"]},
        )

    def test_replace_pull_request_labels(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.replace_labels("owner", "repo", 1, ["ready"])
        mock_client.request.assert_called_with(
            "PUT",
            "/repos/owner/repo/pulls/1/labels",
            params=None,
            json={"labels": ["ready"]},
            data=None,
        )

    def test_delete_pull_request_label(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.delete_label("owner", "repo", 1, "bug")
        mock_client.request.assert_called_with(
            "DELETE",
            "/repos/owner/repo/pulls/1/labels/bug",
            params=None,
        )

    def test_get_pull_request_comment(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.get_comment("owner", "repo", 9)
        mock_client._get.assert_called_with("/repos/owner/repo/pulls/comments/9")

    def test_update_pull_request_comment(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.update_comment("owner", "repo", 9, "edited")
        mock_client.request.assert_called_with(
            "PATCH",
            "/repos/owner/repo/pulls/comments/9",
            params=None,
            json={"body": "edited"},
            data=None,
        )

    def test_delete_pull_request_comment(self, mock_client):
        pulls = PullRequests(mock_client)
        pulls.delete_comment("owner", "repo", 9)
        mock_client.request.assert_called_with(
            "DELETE",
            "/repos/owner/repo/pulls/comments/9",
            params=None,
        )
