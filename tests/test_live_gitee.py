import os

import pytest

from gitee import GiteeClient

pytestmark = pytest.mark.live


def _client_from_env():
    token = os.getenv("GITEE_TOKEN")
    if not token:
        pytest.skip("GITEE_TOKEN is required for live tests")
    return GiteeClient(token=token)


def test_live_current_user_returns_identity():
    with _client_from_env() as client:
        user = client.users.get()
    assert isinstance(user, dict)
    assert user.get("login") or user.get("name")


def test_live_public_repository_details_are_readable():
    with _client_from_env() as client:
        repo = client.repositories.get("oschina", "git-osc")
    assert isinstance(repo, dict)
    assert repo.get("path") or repo.get("name")


def test_live_public_repository_branches_are_readable():
    with _client_from_env() as client:
        branches = client.repositories.list_branches(
            "oschina",
            "git-osc",
            page=1,
            per_page=5,
        )
    assert isinstance(branches, list)
