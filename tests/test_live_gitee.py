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


def test_live_public_repository_readme_and_contents_are_readable():
    with _client_from_env() as client:
        readme = client.repositories.get_readme("oschina", "git-osc")
        contents = client.repositories.get_contents("oschina", "git-osc")
    assert readme
    assert contents


def test_live_public_repository_compare_and_release_list_are_readable():
    with _client_from_env() as client:
        branches = client.repositories.list_branches(
            "oschina",
            "git-osc",
            page=1,
            per_page=1,
        )
        assert branches

        branch = branches[0]["name"]
        comparison = client.repositories.compare_commits(
            "oschina",
            "git-osc",
            branch,
            branch,
        )
        releases = client.repositories.list_releases(
            "oschina",
            "git-osc",
            per_page=1,
        )
    assert comparison
    assert isinstance(releases, list)


def test_live_owned_repository_file_and_release_round_trip():
    target = os.environ.get("GITEE_LIVE_MUTATION_REPO")
    if not target:
        pytest.skip("GITEE_LIVE_MUTATION_REPO is required for mutation live tests")

    owner, repo = target.split("/", 1)
    with _client_from_env() as client:
        path = "sdk-live-smoke.txt"
        created = client.repositories.create_file(
            owner,
            repo,
            path,
            content="hello",
            message="sdk live create file",
        )
        sha = created["content"]["sha"]

        updated = client.repositories.update_file(
            owner,
            repo,
            path,
            content="hello again",
            message="sdk live update file",
            sha=sha,
        )
        updated_sha = updated["content"]["sha"]

        client.repositories.delete_file(
            owner,
            repo,
            path,
            message="sdk live delete file",
            sha=updated_sha,
        )

        release = client.repositories.create_release(
            owner,
            repo,
            tag_name="sdk-live-smoke",
            name="SDK live smoke",
            body="temporary release created by SDK tests",
        )
        client.repositories.delete_release(owner, repo, release["id"])
