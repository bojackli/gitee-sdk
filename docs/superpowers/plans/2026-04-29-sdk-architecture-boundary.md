# SDK Architecture Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the SDK toward clearer resource boundaries while preserving the existing public API and adding explicit pagination plus controlled live API feedback.

**Architecture:** Keep `GiteeClient` responsible for transport, `Resource` responsible for shared SDK helpers, and concrete resources responsible for mapping method arguments to Gitee API requests. Split repository-adjacent behavior into internal helper modules while keeping calls such as `client.repositories.list_commits(...)` working.

**Tech Stack:** Python 3.8+, `requests`, `pytest`, `pytest-cov`, Black, isort.

---

## File Structure

- Modify `gitee/resources/base.py`: add `_require`, `_params`, `_json`, and `_paginated` helpers; keep HTTP verb wrappers.
- Modify `gitee/resources/repositories.py`: keep public methods, delegate branch/commit/collaborator behavior to internal helpers.
- Create `gitee/resources/branches.py`: branch list/get operations.
- Create `gitee/resources/commits.py`: commit list/get operations.
- Create `gitee/resources/collaborators.py`: collaborator list/add/remove operations.
- Modify `tests/test_repositories.py`: add characterization tests for existing repository, branch, commit, collaborator, fork, raw-file methods.
- Create `tests/test_resource_helpers.py`: cover shared helper behavior and `PaginatedList` construction.
- Create `tests/test_client_integration.py`: use fake response/session objects to cover response parsing, API errors, rate-limit handling, and pagination iteration without network access.
- Create `tests/test_live_gitee.py`: marked live tests for stable read-only Gitee API calls.
- Modify `pyproject.toml`: register the `live` pytest marker.
- Modify `DESIGN.md`: align architecture docs with the actual split and test strategy.

## Task 1: Characterize Existing Repository Behavior

**Files:**
- Modify: `tests/test_repositories.py`
- Exercise: `gitee/resources/repositories.py`

- [ ] **Step 1: Add characterization tests for methods that will move internally**

Append these tests to `tests/test_repositories.py`:

```python
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
```

- [ ] **Step 2: Run the characterization tests**

Run:

```bash
pytest tests/test_repositories.py -v
```

Expected: all repository tests pass before refactoring.

- [ ] **Step 3: Commit**

```bash
git add tests/test_repositories.py
git commit -m "test: characterize repository resource behavior"
```

## Task 2: Add Shared Resource Helpers

**Files:**
- Modify: `gitee/resources/base.py`
- Create: `tests/test_resource_helpers.py`

- [ ] **Step 1: Write tests for Resource helpers**

Create `tests/test_resource_helpers.py`:

```python
import pytest
from unittest.mock import Mock

from gitee.exceptions import ValidationError
from gitee.resources.base import PaginatedList, Resource


class TestResourceHelpers:
    def test_require_accepts_present_values(self):
        resource = Resource(Mock())
        resource._require(owner="owner", repo="repo")

    def test_require_rejects_none_values(self):
        resource = Resource(Mock())
        with pytest.raises(ValidationError, match="owner"):
            resource._require(owner=None, repo="repo")

    def test_params_filters_none_values(self):
        resource = Resource(Mock())
        assert resource._params(state="open", page=None, per_page=20) == {
            "state": "open",
            "per_page": 20,
        }

    def test_json_filters_none_values(self):
        resource = Resource(Mock())
        assert resource._json(title="Issue", body=None, labels=["bug"]) == {
            "title": "Issue",
            "labels": ["bug"],
        }

    def test_paginated_builds_paginated_list(self):
        client = Mock()
        resource = Resource(client)
        paginated = resource._paginated(
            "/repos/owner/repo/commits",
            params={"sha": "main"},
        )
        assert isinstance(paginated, PaginatedList)
        assert paginated.client is client
        assert paginated.url == "/repos/owner/repo/commits"
        assert paginated.params == {"sha": "main"}
```

- [ ] **Step 2: Run the new tests and verify failure**

Run:

```bash
pytest tests/test_resource_helpers.py -v
```

Expected: fails because `_require`, `_params`, `_json`, and `_paginated` are not defined.

- [ ] **Step 3: Implement Resource helpers**

Add these methods inside `class Resource` in `gitee/resources/base.py`, after `__init__`:

```python
    def _require(self, **params: Any) -> None:
        """Validate required parameters passed as keyword arguments."""
        missing = [name for name, value in params.items() if value is None]
        if missing:
            from gitee.exceptions import ValidationError

            raise ValidationError(
                f"Missing required parameters: {', '.join(missing)}"
            )

    def _params(self, **params: Any) -> Dict[str, Any]:
        """Build query params without None values."""
        return {key: value for key, value in params.items() if value is not None}

    def _json(self, **data: Any) -> Dict[str, Any]:
        """Build JSON body data without None values."""
        return {key: value for key, value in data.items() if value is not None}

    def _paginated(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        item_key: Optional[str] = None,
    ) -> "PaginatedList":
        """Create a paginated list for a resource endpoint."""
        return PaginatedList(self.client, url, params=params, item_key=item_key)
```

- [ ] **Step 4: Run helper and existing resource tests**

Run:

```bash
pytest tests/test_resource_helpers.py tests/test_repositories.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add gitee/resources/base.py tests/test_resource_helpers.py
git commit -m "feat: add shared resource helpers"
```

## Task 3: Split Branch Operations Internally

**Files:**
- Create: `gitee/resources/branches.py`
- Modify: `gitee/resources/repositories.py`
- Test: `tests/test_repositories.py`

- [ ] **Step 1: Create the internal branch resource**

Create `gitee/resources/branches.py`:

```python
"""Branch resource helpers."""

from typing import Any, Dict, List, Optional

from gitee.resources.base import PaginatedList, Resource


class Branches(Resource):
    """Internal branch operations used by repository resources."""

    def list(
        self,
        owner: str,
        repo: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._require(owner=owner, repo=repo)
        params = self._params(page=page, per_page=per_page)
        return self._get(f"/repos/{owner}/{repo}/branches", params=params)

    def list_paginated(
        self,
        owner: str,
        repo: str,
        per_page: Optional[int] = None,
    ) -> PaginatedList:
        self._require(owner=owner, repo=repo)
        params = self._params(per_page=per_page)
        return self._paginated(f"/repos/{owner}/{repo}/branches", params=params)

    def get(self, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, branch=branch)
        return self._get(f"/repos/{owner}/{repo}/branches/{branch}")
```

- [ ] **Step 2: Wire Branches into Repositories**

In `gitee/resources/repositories.py`, add:

```python
from gitee.resources.branches import Branches
```

Add this to `Repositories`:

```python
    def __init__(self, client: Any) -> None:
        super().__init__(client)
        self._branches = Branches(client)
```

Replace `list_branches` with:

```python
    def list_branches(
        self,
        owner: str,
        repo: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库分支列表。"""
        return self._branches.list(owner, repo, page=page, per_page=per_page)
```

Replace `get_branch` with:

```python
    def get_branch(self, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        """获取仓库分支详情。"""
        return self._branches.get(owner, repo, branch)
```

Add:

```python
    def list_branches_paginated(
        self,
        owner: str,
        repo: str,
        per_page: Optional[int] = None,
    ) -> PaginatedList:
        """获取可迭代分页仓库分支列表。"""
        return self._branches.list_paginated(owner, repo, per_page=per_page)
```

- [ ] **Step 3: Run repository tests**

Run:

```bash
pytest tests/test_repositories.py -v
```

Expected: all tests pass and public method behavior remains unchanged.

- [ ] **Step 4: Commit**

```bash
git add gitee/resources/branches.py gitee/resources/repositories.py
git commit -m "refactor: split branch operations from repositories"
```

## Task 4: Split Commit Operations Internally

**Files:**
- Create: `gitee/resources/commits.py`
- Modify: `gitee/resources/repositories.py`
- Test: `tests/test_repositories.py`

- [ ] **Step 1: Create the internal commit resource**

Create `gitee/resources/commits.py`:

```python
"""Commit resource helpers."""

from typing import Any, Dict, List, Optional

from gitee.resources.base import PaginatedList, Resource


class Commits(Resource):
    """Internal commit operations used by repository resources."""

    def list(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        author: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._require(owner=owner, repo=repo)
        params = self._params(
            sha=sha,
            path=path,
            author=author,
            since=since,
            until=until,
            page=page,
            per_page=per_page,
        )
        return self._get(f"/repos/{owner}/{repo}/commits", params=params)

    def list_paginated(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        author: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        per_page: Optional[int] = None,
    ) -> PaginatedList:
        self._require(owner=owner, repo=repo)
        params = self._params(
            sha=sha,
            path=path,
            author=author,
            since=since,
            until=until,
            per_page=per_page,
        )
        return self._paginated(f"/repos/{owner}/{repo}/commits", params=params)

    def get(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, sha=sha)
        return self._get(f"/repos/{owner}/{repo}/commits/{sha}")
```

- [ ] **Step 2: Wire Commits into Repositories**

In `gitee/resources/repositories.py`, add:

```python
from gitee.resources.commits import Commits
```

Update `__init__`:

```python
        self._commits = Commits(client)
```

Replace `list_commits` with:

```python
    def list_commits(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        author: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库提交列表。"""
        return self._commits.list(
            owner,
            repo,
            sha=sha,
            path=path,
            author=author,
            since=since,
            until=until,
            page=page,
            per_page=per_page,
        )
```

Replace the duplicate `get_commit` implementation with:

```python
    def get_commit(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """获取仓库提交详情。"""
        return self._commits.get(owner, repo, sha)
```

Add:

```python
    def list_commits_paginated(
        self,
        owner: str,
        repo: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        author: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None,
        per_page: Optional[int] = None,
    ) -> PaginatedList:
        """获取可迭代分页仓库提交列表。"""
        return self._commits.list_paginated(
            owner,
            repo,
            sha=sha,
            path=path,
            author=author,
            since=since,
            until=until,
            per_page=per_page,
        )
```

- [ ] **Step 3: Remove the earlier duplicate `get_commit` block**

`repositories.py` currently defines `get_commit` twice. Keep one public `get_commit` method that delegates to `self._commits.get(...)`.

- [ ] **Step 4: Run repository tests**

Run:

```bash
pytest tests/test_repositories.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add gitee/resources/commits.py gitee/resources/repositories.py
git commit -m "refactor: split commit operations from repositories"
```

## Task 5: Split Collaborator Operations Internally

**Files:**
- Create: `gitee/resources/collaborators.py`
- Modify: `gitee/resources/repositories.py`
- Test: `tests/test_repositories.py`

- [ ] **Step 1: Create the internal collaborator resource**

Create `gitee/resources/collaborators.py`:

```python
"""Collaborator resource helpers."""

from typing import Any, Dict, List, Optional

from gitee.resources.base import Resource


class Collaborators(Resource):
    """Internal collaborator operations used by repository resources."""

    def list(
        self,
        owner: str,
        repo: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._require(owner=owner, repo=repo)
        params = self._params(page=page, per_page=per_page)
        return self._get(f"/repos/{owner}/{repo}/collaborators", params=params)

    def add(
        self,
        owner: str,
        repo: str,
        username: str,
        permission: Optional[str] = None,
    ) -> None:
        self._require(owner=owner, repo=repo, username=username)
        data = self._json(permission=permission)
        self._put(f"/repos/{owner}/{repo}/collaborators/{username}", json=data)

    def remove(self, owner: str, repo: str, username: str) -> None:
        self._require(owner=owner, repo=repo, username=username)
        self._delete(f"/repos/{owner}/{repo}/collaborators/{username}")
```

- [ ] **Step 2: Wire Collaborators into Repositories**

In `gitee/resources/repositories.py`, add:

```python
from gitee.resources.collaborators import Collaborators
```

Update `__init__`:

```python
        self._collaborators = Collaborators(client)
```

Replace collaborator public methods with:

```python
    def list_collaborators(
        self,
        owner: str,
        repo: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """获取仓库协作者列表。"""
        return self._collaborators.list(owner, repo, page=page, per_page=per_page)

    def add_collaborator(
        self,
        owner: str,
        repo: str,
        username: str,
        permission: Optional[str] = None,
    ) -> None:
        """添加仓库协作者。"""
        self._collaborators.add(owner, repo, username, permission=permission)

    def remove_collaborator(self, owner: str, repo: str, username: str) -> None:
        """移除仓库协作者。"""
        self._collaborators.remove(owner, repo, username)
```

- [ ] **Step 3: Run repository tests**

Run:

```bash
pytest tests/test_repositories.py -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit**

```bash
git add gitee/resources/collaborators.py gitee/resources/repositories.py
git commit -m "refactor: split collaborator operations from repositories"
```

## Task 6: Add Explicit Paginated Repository Lists

**Files:**
- Modify: `gitee/resources/repositories.py`
- Modify: `tests/test_repositories.py`

- [ ] **Step 1: Add tests for paginated methods**

Append to `tests/test_repositories.py`:

```python
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
```

- [ ] **Step 2: Run tests and verify only `list_paginated` is missing**

Run:

```bash
pytest tests/test_repositories.py -v
```

Expected: tests for branch and commit paginated methods pass if previous tasks added them; `test_list_repos_paginated` fails until implemented.

- [ ] **Step 3: Implement `Repositories.list_paginated`**

Add to `Repositories`:

```python
    def list_paginated(
        self,
        owner: str,
        type: Optional[str] = None,
        sort: Optional[str] = None,
        direction: Optional[str] = None,
        per_page: Optional[int] = None,
        **kwargs: Any,
    ) -> PaginatedList:
        """获取可迭代分页仓库列表。"""
        self._require(owner=owner)
        params = self._params(
            type=type,
            sort=sort,
            direction=direction,
            per_page=per_page,
            **kwargs,
        )
        return self._paginated(f"/users/{owner}/repos", params=params)
```

- [ ] **Step 4: Run repository tests**

Run:

```bash
pytest tests/test_repositories.py -v
```

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add gitee/resources/repositories.py tests/test_repositories.py
git commit -m "feat: add explicit repository pagination methods"
```

## Task 7: Add Client Integration Tests Without Network

**Files:**
- Create: `tests/test_client_integration.py`
- Exercise: `gitee/client.py`, `gitee/resources/base.py`

- [ ] **Step 1: Create fake response and session tests**

Create `tests/test_client_integration.py`:

```python
import pytest
import requests

from gitee.client import GiteeClient
from gitee.exceptions import APIError, RateLimitExceeded
from gitee.resources.base import PaginatedList


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", headers=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.headers = headers or {}
        self.content = text.encode("utf-8") if text else b"x"

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.exceptions.HTTPError("HTTP error")
            error.response = self
            raise error


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.headers = {}
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)

    def close(self):
        pass


def test_client_parses_json_response():
    client = GiteeClient()
    client.session = FakeSession([FakeResponse(payload={"id": 1})])
    assert client.request("GET", "/user") == {"id": 1}
    assert client.session.calls[0]["url"] == "https://gitee.com/api/v5/user"


def test_client_returns_text_for_non_json_response():
    client = GiteeClient()
    client.session = FakeSession([FakeResponse(payload=ValueError(), text="raw")])
    assert client.request("GET", "/raw") == "raw"


def test_client_returns_none_for_204_response():
    response = FakeResponse(status_code=204, payload=None, text="")
    response.content = b""
    client = GiteeClient()
    client.session = FakeSession([response])
    assert client.request("DELETE", "/resource") is None


def test_client_maps_api_error():
    client = GiteeClient()
    client.session = FakeSession(
        [FakeResponse(status_code=404, payload={"message": "Not found"})]
    )
    with pytest.raises(APIError) as exc:
        client.request("GET", "/missing")
    assert exc.value.status_code == 404
    assert exc.value.message == "Not found"


def test_client_raises_rate_limit_after_successful_response():
    client = GiteeClient()
    client.session = FakeSession(
        [
            FakeResponse(
                payload={"ok": True},
                headers={
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "123",
                },
            )
        ]
    )
    with pytest.raises(RateLimitExceeded) as exc:
        client.request("GET", "/limited")
    assert exc.value.reset_time == "123"


def test_paginated_list_fetches_until_empty_page():
    client = GiteeClient()
    client.session = FakeSession(
        [
            FakeResponse(payload=[{"id": 1}, {"id": 2}]),
            FakeResponse(payload=[]),
        ]
    )
    paginated = PaginatedList(client, "/items", params={"state": "open"})
    assert paginated.all() == [{"id": 1}, {"id": 2}]
    assert client.session.calls[0]["params"] == {
        "state": "open",
        "page": 1,
        "per_page": 20,
    }
    assert client.session.calls[1]["params"] == {
        "state": "open",
        "page": 2,
        "per_page": 20,
    }
```

- [ ] **Step 2: Run integration tests**

Run:

```bash
pytest tests/test_client_integration.py -v
```

Expected: tests pass without real network access.

- [ ] **Step 3: Run all non-live tests**

Run:

```bash
pytest -m "not live" -v
```

Expected: all non-live tests pass.

- [ ] **Step 4: Commit**

```bash
git add tests/test_client_integration.py
git commit -m "test: add client integration coverage"
```

## Task 8: Add Controlled Live Tests

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/test_live_gitee.py`

- [ ] **Step 1: Register the live marker**

Add this section to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "live: tests that call the real Gitee API and require GITEE_TOKEN",
]
```

- [ ] **Step 2: Add live read-only tests**

Create `tests/test_live_gitee.py`:

```python
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
```

- [ ] **Step 3: Run non-live tests and ensure live tests are excluded by marker expression**

Run:

```bash
pytest -m "not live" -v
```

Expected: non-live tests pass and live tests are deselected.

- [ ] **Step 4: Run live tests when token is available**

Run:

```bash
GITEE_TOKEN="$GITEE_TOKEN" pytest -m live -v
```

Expected with `GITEE_TOKEN`: live tests pass against real Gitee read-only endpoints. Expected without `GITEE_TOKEN`: live tests skip.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml tests/test_live_gitee.py
git commit -m "test: add controlled live gitee tests"
```

## Task 9: Update Architecture Documentation

**Files:**
- Modify: `DESIGN.md`
- Verify: `docs/superpowers/specs/2026-04-29-sdk-architecture-boundary-design.md`

- [ ] **Step 1: Update the architecture section**

In `DESIGN.md`, update the resource tree to include:

```text
gitee/resources/
├── base.py
├── repositories.py
├── branches.py
├── commits.py
├── collaborators.py
├── issues.py
├── pulls.py
└── ...
```

Remove references to `git_data.py` as an active module.

- [ ] **Step 2: Add the boundary summary**

Add this summary under the core component section:

```markdown
`GiteeClient` owns transport concerns: session setup, authentication headers,
request dispatch, response parsing, rate-limit checks, and exception mapping.
`Resource` owns shared SDK helpers such as HTTP verb wrappers, required
parameter checks, filtered parameter/body construction, and pagination
construction. Concrete resources map method arguments to API paths, query
parameters, and request bodies.
```

- [ ] **Step 3: Add the testing strategy**

Add this testing summary:

```markdown
Tests are split into unit tests, integration tests, and live tests. Unit tests
mock resource clients and verify generated paths, params, methods, and bodies.
Integration tests use fake HTTP sessions and responses to verify client
behavior without network access. Live tests are marked with `pytest.mark.live`,
read `GITEE_TOKEN` from the environment, and cover stable read-only Gitee API
calls.
```

- [ ] **Step 4: Run documentation-adjacent checks**

Run:

```bash
pytest -m "not live" -v
```

Expected: all non-live tests pass after documentation changes.

- [ ] **Step 5: Commit**

```bash
git add DESIGN.md
git commit -m "docs: align design with resource boundary refactor"
```

## Task 10: Final Verification

**Files:**
- Verify all changed source, tests, and docs.

- [ ] **Step 1: Format source and tests**

Run:

```bash
black gitee tests
isort gitee tests
```

Expected: formatting completes without errors.

- [ ] **Step 2: Run full non-live test suite**

Run:

```bash
pytest -m "not live" -v
```

Expected: all non-live tests pass.

- [ ] **Step 3: Run type checking**

Run:

```bash
mypy gitee
```

Expected: no type errors in `gitee`.

- [ ] **Step 4: Run live tests if credentials are available**

Run:

```bash
GITEE_TOKEN="$GITEE_TOKEN" pytest -m live -v
```

Expected with `GITEE_TOKEN`: live tests pass. Expected without `GITEE_TOKEN`: tests skip with the explicit token message.

- [ ] **Step 5: Inspect the final diff**

Run:

```bash
git status --short
git diff --stat HEAD
```

Expected: only intended source, test, and documentation changes remain.

- [ ] **Step 6: Commit any final formatting or documentation drift**

If formatting changed files after the previous commits, run:

```bash
git add gitee tests DESIGN.md pyproject.toml
git commit -m "chore: finalize resource boundary refactor"
```

If no files changed, do not create an empty commit.
