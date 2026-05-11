# Priority API Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the high-priority Gitee repository automation endpoints needed for file changes, branch governance, PR workflow completion, and releases.

**Architecture:** Keep the public API under `client.repositories` and `client.pulls`. Add focused internal resources for repository content and releases, expand existing branch/collaborator resources, and keep PR workflow methods in `gitee/resources/pulls.py` unless the file becomes too large during implementation.

**Tech Stack:** Python, requests-backed `GiteeClient`, pytest, black, isort, mypy.

---

## File Map

- Create: `gitee/resources/contents.py` for README, contents, file mutation, compare, blame, and multi-file commit helpers.
- Create: `gitee/resources/releases.py` for Release CRUD and attachment list/get/delete/download.
- Modify: `gitee/resources/repositories.py` to delegate new repository methods.
- Modify: `gitee/resources/branches.py` for branch creation and protection endpoints.
- Modify: `gitee/resources/collaborators.py` for collaborator membership and permission reads.
- Modify: `gitee/resources/pulls.py` for PR merge status, review/test assignment, linked issues, labels, and comment mutation.
- Test: `tests/test_repositories.py`, `tests/test_pulls.py`, and `tests/test_live_gitee.py`.

## Task 1: Repository Content Resource

**Files:**
- Create: `gitee/resources/contents.py`
- Modify: `gitee/resources/repositories.py`
- Test: `tests/test_repositories.py`

- [ ] **Step 1: Write failing repository content tests**

Add these tests to `tests/test_repositories.py`:

```python
def test_get_readme(mock_client):
    repos = Repositories(mock_client)
    repos.get_readme("owner", "repo", ref="main")
    mock_client._get.assert_called_with(
        "/repos/owner/repo/readme",
        params={"ref": "main"},
    )


def test_get_contents_defaults_to_root(mock_client):
    repos = Repositories(mock_client)
    repos.get_contents("owner", "repo")
    mock_client._get.assert_called_with(
        "/repos/owner/repo/contents",
        params={},
    )


def test_get_contents_with_path_and_ref(mock_client):
    repos = Repositories(mock_client)
    repos.get_contents("owner", "repo", "src/app.py", ref="main")
    mock_client._get.assert_called_with(
        "/repos/owner/repo/contents/src/app.py",
        params={"ref": "main"},
    )


def test_create_file(mock_client):
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


def test_update_file(mock_client):
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


def test_delete_file(mock_client):
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


def test_create_commit(mock_client):
    repos = Repositories(mock_client)
    files = [{"path": "a.txt", "content": "A"}]
    repos.create_commit("owner", "repo", files=files, message="batch", branch="main")
    mock_client._post.assert_called_with(
        "/repos/owner/repo/commits",
        json={"files": files, "message": "batch", "branch": "main"},
    )


def test_compare_commits(mock_client):
    repos = Repositories(mock_client)
    repos.compare_commits("owner", "repo", "main", "feature")
    mock_client._get.assert_called_with("/repos/owner/repo/compare/main...feature")


def test_get_blame(mock_client):
    repos = Repositories(mock_client)
    repos.get_blame("owner", "repo", "README.md", ref="main")
    mock_client._get.assert_called_with(
        "/repos/owner/repo/blame/README.md",
        params={"ref": "main"},
    )
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest tests/test_repositories.py -q
```

Expected: fails with `AttributeError` for the new `Repositories` methods.

- [ ] **Step 3: Implement `Contents` resource**

Create `gitee/resources/contents.py`:

```python
"""Repository content and commit automation helpers."""

from typing import Any, Dict, List, Optional

from gitee.resources.base import Resource


class Contents(Resource):
    """Repository content, file mutation, compare, and blame endpoints."""

    def get_readme(
        self, owner: str, repo: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo)
        return self._get(
            f"/repos/{owner}/{repo}/readme",
            params=self._params(ref=ref),
        )

    def get(
        self, owner: str, repo: str, path: str = "", ref: Optional[str] = None
    ) -> Any:
        self._require(owner=owner, repo=repo)
        url = f"/repos/{owner}/{repo}/contents"
        if path:
            url = f"{url}/{path}"
        return self._get(url, params=self._params(ref=ref))

    def create_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, path=path, content=content, message=message)
        data = self._json(content=content, message=message, branch=branch, **kwargs)
        return self._post(f"/repos/{owner}/{repo}/contents/{path}", json=data)

    def update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        sha: str,
        branch: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        self._require(
            owner=owner, repo=repo, path=path, content=content, message=message, sha=sha
        )
        data = self._json(
            content=content, message=message, sha=sha, branch=branch, **kwargs
        )
        return self._put(f"/repos/{owner}/{repo}/contents/{path}", json=data)

    def delete_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        sha: str,
        branch: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        self._require(owner=owner, repo=repo, path=path, message=message, sha=sha)
        data = self._json(message=message, sha=sha, branch=branch, **kwargs)
        return self._delete(f"/repos/{owner}/{repo}/contents/{path}", json=data)

    def create_commit(
        self,
        owner: str,
        repo: str,
        files: List[Dict[str, Any]],
        message: str,
        branch: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, files=files, message=message)
        data = self._json(files=files, message=message, branch=branch, **kwargs)
        return self._post(f"/repos/{owner}/{repo}/commits", json=data)

    def compare(self, owner: str, repo: str, base: str, head: str) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, base=base, head=head)
        return self._get(f"/repos/{owner}/{repo}/compare/{base}...{head}")

    def blame(
        self, owner: str, repo: str, path: str, ref: Optional[str] = None
    ) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, path=path)
        return self._get(
            f"/repos/{owner}/{repo}/blame/{path}",
            params=self._params(ref=ref),
        )
```

- [ ] **Step 4: Delegate through `Repositories`**

In `gitee/resources/repositories.py`, import `Contents`, instantiate it in
`__init__`, and add public forwarding methods:

```python
from gitee.resources.contents import Contents
```

```python
self._contents = Contents(client)
```

```python
def get_readme(
    self, owner: str, repo: str, ref: Optional[str] = None
) -> Dict[str, Any]:
    """获取仓库 README。"""
    return self._contents.get_readme(owner, repo, ref=ref)

def get_contents(
    self, owner: str, repo: str, path: str = "", ref: Optional[str] = None
) -> Any:
    """获取仓库路径内容。"""
    return self._contents.get(owner, repo, path=path, ref=ref)

def create_file(
    self,
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """在仓库中新建文件。"""
    return self._contents.create_file(
        owner, repo, path, content, message, branch=branch, **kwargs
    )

def update_file(
    self,
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    sha: str,
    branch: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """更新仓库文件。"""
    return self._contents.update_file(
        owner, repo, path, content, message, sha, branch=branch, **kwargs
    )

def delete_file(
    self,
    owner: str,
    repo: str,
    path: str,
    message: str,
    sha: str,
    branch: Optional[str] = None,
    **kwargs: Any,
) -> Any:
    """删除仓库文件。"""
    return self._contents.delete_file(
        owner, repo, path, message, sha, branch=branch, **kwargs
    )

def create_commit(
    self,
    owner: str,
    repo: str,
    files: List[Dict[str, Any]],
    message: str,
    branch: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """提交多个文件变更。"""
    return self._contents.create_commit(
        owner, repo, files, message, branch=branch, **kwargs
    )

def compare_commits(
    self, owner: str, repo: str, base: str, head: str
) -> Dict[str, Any]:
    """对比两个提交或分支。"""
    return self._contents.compare(owner, repo, base, head)

def get_blame(
    self, owner: str, repo: str, path: str, ref: Optional[str] = None
) -> Dict[str, Any]:
    """获取文件 blame 信息。"""
    return self._contents.blame(owner, repo, path, ref=ref)
```

- [ ] **Step 5: Verify and commit**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest tests/test_repositories.py -q
```

Expected: repository tests pass.

Commit:

```bash
git add gitee/resources/contents.py gitee/resources/repositories.py tests/test_repositories.py
git commit -m "feat: add repository content APIs"
```

## Task 2: Branch And Collaborator Governance

**Files:**
- Modify: `gitee/resources/branches.py`
- Modify: `gitee/resources/collaborators.py`
- Modify: `gitee/resources/repositories.py`
- Test: `tests/test_repositories.py`

- [ ] **Step 1: Write failing branch and collaborator tests**

Add these tests to `tests/test_repositories.py`:

```python
def test_create_branch(mock_client):
    repos = Repositories(mock_client)
    repos.create_branch("owner", "repo", refs="main", branch_name="feature")
    mock_client._post.assert_called_with(
        "/repos/owner/repo/branches",
        json={"refs": "main", "branch_name": "feature"},
    )


def test_protect_branch(mock_client):
    repos = Repositories(mock_client)
    repos.protect_branch("owner", "repo", "main", pushers=["alice"])
    mock_client.request.assert_called_with(
        "PUT",
        "/repos/owner/repo/branches/main/protection",
        params=None,
        json={"pushers": ["alice"]},
        data=None,
    )


def test_unprotect_branch(mock_client):
    repos = Repositories(mock_client)
    repos.unprotect_branch("owner", "repo", "main")
    mock_client.request.assert_called_with(
        "DELETE",
        "/repos/owner/repo/branches/main/protection",
        params=None,
    )


def test_create_branch_protection_rule(mock_client):
    repos = Repositories(mock_client)
    repos.create_branch_protection_rule("owner", "repo", "release/*", can_push=True)
    mock_client.request.assert_called_with(
        "PUT",
        "/repos/owner/repo/branches/setting/new",
        params=None,
        json={"wildcard": "release/*", "can_push": True},
        data=None,
    )


def test_update_branch_protection_rule(mock_client):
    repos = Repositories(mock_client)
    repos.update_branch_protection_rule("owner", "repo", "release/*", can_push=False)
    mock_client.request.assert_called_with(
        "PUT",
        "/repos/owner/repo/branches/release/*/setting",
        params=None,
        json={"can_push": False},
        data=None,
    )


def test_delete_branch_protection_rule(mock_client):
    repos = Repositories(mock_client)
    repos.delete_branch_protection_rule("owner", "repo", "release/*")
    mock_client.request.assert_called_with(
        "DELETE",
        "/repos/owner/repo/branches/release/*/setting",
        params=None,
    )


def test_is_collaborator(mock_client):
    repos = Repositories(mock_client)
    repos.is_collaborator("owner", "repo", "alice")
    mock_client._get.assert_called_with("/repos/owner/repo/collaborators/alice")


def test_get_collaborator_permission(mock_client):
    repos = Repositories(mock_client)
    repos.get_collaborator_permission("owner", "repo", "alice")
    mock_client._get.assert_called_with(
        "/repos/owner/repo/collaborators/alice/permission"
    )
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest tests/test_repositories.py -q
```

Expected: fails with `AttributeError` for new repository methods.

- [ ] **Step 3: Expand `Branches`**

In `gitee/resources/branches.py`, add:

```python
from typing import Any
```

```python
def create(
    self, owner: str, repo: str, refs: str, branch_name: str
) -> Dict[str, Any]:
    self._require(owner=owner, repo=repo, refs=refs, branch_name=branch_name)
    data = self._json(refs=refs, branch_name=branch_name)
    return self._post(f"/repos/{owner}/{repo}/branches", json=data)

def protect(self, owner: str, repo: str, branch: str, **kwargs: Any) -> Any:
    self._require(owner=owner, repo=repo, branch=branch)
    return self._put(
        f"/repos/{owner}/{repo}/branches/{branch}/protection",
        json=self._json(**kwargs),
    )

def unprotect(self, owner: str, repo: str, branch: str) -> Any:
    self._require(owner=owner, repo=repo, branch=branch)
    return self._delete(f"/repos/{owner}/{repo}/branches/{branch}/protection")

def create_protection_rule(
    self, owner: str, repo: str, wildcard: str, **kwargs: Any
) -> Any:
    self._require(owner=owner, repo=repo, wildcard=wildcard)
    data = self._json(wildcard=wildcard, **kwargs)
    return self._put(f"/repos/{owner}/{repo}/branches/setting/new", json=data)

def update_protection_rule(
    self, owner: str, repo: str, wildcard: str, **kwargs: Any
) -> Any:
    self._require(owner=owner, repo=repo, wildcard=wildcard)
    return self._put(
        f"/repos/{owner}/{repo}/branches/{wildcard}/setting",
        json=self._json(**kwargs),
    )

def delete_protection_rule(self, owner: str, repo: str, wildcard: str) -> Any:
    self._require(owner=owner, repo=repo, wildcard=wildcard)
    return self._delete(f"/repos/{owner}/{repo}/branches/{wildcard}/setting")
```

- [ ] **Step 4: Expand `Collaborators`**

In `gitee/resources/collaborators.py`, add:

```python
def is_collaborator(self, owner: str, repo: str, username: str) -> Any:
    self._require(owner=owner, repo=repo, username=username)
    return self._get(f"/repos/{owner}/{repo}/collaborators/{username}")

def get_permission(self, owner: str, repo: str, username: str) -> Dict[str, Any]:
    self._require(owner=owner, repo=repo, username=username)
    return self._get(f"/repos/{owner}/{repo}/collaborators/{username}/permission")
```

- [ ] **Step 5: Delegate through `Repositories`**

Add these methods to `gitee/resources/repositories.py`:

```python
def create_branch(
    self, owner: str, repo: str, refs: str, branch_name: str
) -> Dict[str, Any]:
    """创建仓库分支。"""
    return self._branches.create(owner, repo, refs, branch_name)

def protect_branch(self, owner: str, repo: str, branch: str, **kwargs: Any) -> Any:
    """设置分支保护。"""
    return self._branches.protect(owner, repo, branch, **kwargs)

def unprotect_branch(self, owner: str, repo: str, branch: str) -> Any:
    """取消分支保护。"""
    return self._branches.unprotect(owner, repo, branch)

def create_branch_protection_rule(
    self, owner: str, repo: str, wildcard: str, **kwargs: Any
) -> Any:
    """创建保护分支规则。"""
    return self._branches.create_protection_rule(owner, repo, wildcard, **kwargs)

def update_branch_protection_rule(
    self, owner: str, repo: str, wildcard: str, **kwargs: Any
) -> Any:
    """更新保护分支规则。"""
    return self._branches.update_protection_rule(owner, repo, wildcard, **kwargs)

def delete_branch_protection_rule(self, owner: str, repo: str, wildcard: str) -> Any:
    """删除保护分支规则。"""
    return self._branches.delete_protection_rule(owner, repo, wildcard)

def is_collaborator(self, owner: str, repo: str, username: str) -> Any:
    """判断用户是否为仓库成员。"""
    return self._collaborators.is_collaborator(owner, repo, username)

def get_collaborator_permission(
    self, owner: str, repo: str, username: str
) -> Dict[str, Any]:
    """查看仓库成员权限。"""
    return self._collaborators.get_permission(owner, repo, username)
```

- [ ] **Step 6: Verify and commit**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest tests/test_repositories.py -q
```

Expected: repository tests pass.

Commit:

```bash
git add gitee/resources/branches.py gitee/resources/collaborators.py gitee/resources/repositories.py tests/test_repositories.py
git commit -m "feat: add branch and collaborator governance APIs"
```

## Task 3: Pull Request Workflow Completion

**Files:**
- Modify: `gitee/resources/pulls.py`
- Test: `tests/test_pulls.py`

- [ ] **Step 1: Write failing PR workflow tests**

Add these tests to `tests/test_pulls.py`:

```python
def test_is_merged(mock_client):
    pulls = PullRequests(mock_client)
    pulls.is_merged("owner", "repo", 1)
    mock_client._get.assert_called_with("/repos/owner/repo/pulls/1/merge")


def test_review_pull_request(mock_client):
    pulls = PullRequests(mock_client)
    pulls.review("owner", "repo", 1, event="APPROVE", body="ok")
    mock_client._post.assert_called_with(
        "/repos/owner/repo/pulls/1/review",
        json={"event": "APPROVE", "body": "ok"},
    )


def test_test_pull_request(mock_client):
    pulls = PullRequests(mock_client)
    pulls.test("owner", "repo", 1, event="PASS", body="verified")
    mock_client._post.assert_called_with(
        "/repos/owner/repo/pulls/1/test",
        json={"event": "PASS", "body": "verified"},
    )


def test_assign_reviewers(mock_client):
    pulls = PullRequests(mock_client)
    pulls.assign_reviewers("owner", "repo", 1, ["alice", "bob"])
    mock_client._post.assert_called_with(
        "/repos/owner/repo/pulls/1/assignees",
        json={"assignees": ["alice", "bob"]},
    )


def test_unassign_reviewers(mock_client):
    pulls = PullRequests(mock_client)
    pulls.unassign_reviewers("owner", "repo", 1, ["alice"])
    mock_client.request.assert_called_with(
        "DELETE",
        "/repos/owner/repo/pulls/1/assignees",
        params=None,
        json={"assignees": ["alice"]},
    )


def test_reset_reviewer_state(mock_client):
    pulls = PullRequests(mock_client)
    pulls.reset_reviewer_state("owner", "repo", 1, ["alice"])
    mock_client.request.assert_called_with(
        "PATCH",
        "/repos/owner/repo/pulls/1/assignees",
        params=None,
        json={"assignees": ["alice"]},
        data=None,
    )


def test_assign_testers(mock_client):
    pulls = PullRequests(mock_client)
    pulls.assign_testers("owner", "repo", 1, ["alice"])
    mock_client._post.assert_called_with(
        "/repos/owner/repo/pulls/1/testers",
        json={"testers": ["alice"]},
    )


def test_unassign_testers(mock_client):
    pulls = PullRequests(mock_client)
    pulls.unassign_testers("owner", "repo", 1, ["alice"])
    mock_client.request.assert_called_with(
        "DELETE",
        "/repos/owner/repo/pulls/1/testers",
        params=None,
        json={"testers": ["alice"]},
    )


def test_reset_tester_state(mock_client):
    pulls = PullRequests(mock_client)
    pulls.reset_tester_state("owner", "repo", 1, ["alice"])
    mock_client.request.assert_called_with(
        "PATCH",
        "/repos/owner/repo/pulls/1/testers",
        params=None,
        json={"testers": ["alice"]},
        data=None,
    )


def test_list_pull_request_issues(mock_client):
    pulls = PullRequests(mock_client)
    pulls.list_issues("owner", "repo", 1)
    mock_client._get.assert_called_with("/repos/owner/repo/pulls/1/issues")


def test_list_pull_request_labels(mock_client):
    pulls = PullRequests(mock_client)
    pulls.list_labels("owner", "repo", 1)
    mock_client._get.assert_called_with("/repos/owner/repo/pulls/1/labels")


def test_add_pull_request_labels(mock_client):
    pulls = PullRequests(mock_client)
    pulls.add_labels("owner", "repo", 1, ["bug"])
    mock_client._post.assert_called_with(
        "/repos/owner/repo/pulls/1/labels",
        json={"labels": ["bug"]},
    )


def test_replace_pull_request_labels(mock_client):
    pulls = PullRequests(mock_client)
    pulls.replace_labels("owner", "repo", 1, ["ready"])
    mock_client.request.assert_called_with(
        "PUT",
        "/repos/owner/repo/pulls/1/labels",
        params=None,
        json={"labels": ["ready"]},
        data=None,
    )


def test_delete_pull_request_label(mock_client):
    pulls = PullRequests(mock_client)
    pulls.delete_label("owner", "repo", 1, "bug")
    mock_client.request.assert_called_with(
        "DELETE",
        "/repos/owner/repo/pulls/1/labels/bug",
        params=None,
    )


def test_get_pull_request_comment(mock_client):
    pulls = PullRequests(mock_client)
    pulls.get_comment("owner", "repo", 9)
    mock_client._get.assert_called_with("/repos/owner/repo/pulls/comments/9")


def test_update_pull_request_comment(mock_client):
    pulls = PullRequests(mock_client)
    pulls.update_comment("owner", "repo", 9, "edited")
    mock_client.request.assert_called_with(
        "PATCH",
        "/repos/owner/repo/pulls/comments/9",
        params=None,
        json={"body": "edited"},
        data=None,
    )


def test_delete_pull_request_comment(mock_client):
    pulls = PullRequests(mock_client)
    pulls.delete_comment("owner", "repo", 9)
    mock_client.request.assert_called_with(
        "DELETE",
        "/repos/owner/repo/pulls/comments/9",
        params=None,
    )
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest tests/test_pulls.py -q
```

Expected: fails with `AttributeError` for the new `PullRequests` methods.

- [ ] **Step 3: Implement PR workflow methods**

Add these methods to `gitee/resources/pulls.py`:

```python
def is_merged(self, owner: str, repo: str, number: Union[int, str]) -> Any:
    self._require(owner=owner, repo=repo, number=number)
    return self._get(f"/repos/{owner}/{repo}/pulls/{number}/merge")

def review(
    self,
    owner: str,
    repo: str,
    number: Union[int, str],
    event: str,
    body: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    self._require(owner=owner, repo=repo, number=number, event=event)
    data = self._json(event=event, body=body, **kwargs)
    return self._post(f"/repos/{owner}/{repo}/pulls/{number}/review", json=data)

def test(
    self,
    owner: str,
    repo: str,
    number: Union[int, str],
    event: str,
    body: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    self._require(owner=owner, repo=repo, number=number, event=event)
    data = self._json(event=event, body=body, **kwargs)
    return self._post(f"/repos/{owner}/{repo}/pulls/{number}/test", json=data)

def assign_reviewers(
    self, owner: str, repo: str, number: Union[int, str], assignees: List[str]
) -> Any:
    self._require(owner=owner, repo=repo, number=number, assignees=assignees)
    return self._post(
        f"/repos/{owner}/{repo}/pulls/{number}/assignees",
        json={"assignees": assignees},
    )

def unassign_reviewers(
    self, owner: str, repo: str, number: Union[int, str], assignees: List[str]
) -> Any:
    self._require(owner=owner, repo=repo, number=number, assignees=assignees)
    return self._delete(
        f"/repos/{owner}/{repo}/pulls/{number}/assignees",
        json={"assignees": assignees},
    )

def reset_reviewer_state(
    self, owner: str, repo: str, number: Union[int, str], assignees: List[str]
) -> Any:
    self._require(owner=owner, repo=repo, number=number, assignees=assignees)
    return self._patch(
        f"/repos/{owner}/{repo}/pulls/{number}/assignees",
        json={"assignees": assignees},
    )

def assign_testers(
    self, owner: str, repo: str, number: Union[int, str], testers: List[str]
) -> Any:
    self._require(owner=owner, repo=repo, number=number, testers=testers)
    return self._post(
        f"/repos/{owner}/{repo}/pulls/{number}/testers",
        json={"testers": testers},
    )

def unassign_testers(
    self, owner: str, repo: str, number: Union[int, str], testers: List[str]
) -> Any:
    self._require(owner=owner, repo=repo, number=number, testers=testers)
    return self._delete(
        f"/repos/{owner}/{repo}/pulls/{number}/testers",
        json={"testers": testers},
    )

def reset_tester_state(
    self, owner: str, repo: str, number: Union[int, str], testers: List[str]
) -> Any:
    self._require(owner=owner, repo=repo, number=number, testers=testers)
    return self._patch(
        f"/repos/{owner}/{repo}/pulls/{number}/testers",
        json={"testers": testers},
    )

def list_issues(self, owner: str, repo: str, number: Union[int, str]) -> Any:
    self._require(owner=owner, repo=repo, number=number)
    return self._get(f"/repos/{owner}/{repo}/pulls/{number}/issues")

def list_labels(self, owner: str, repo: str, number: Union[int, str]) -> Any:
    self._require(owner=owner, repo=repo, number=number)
    return self._get(f"/repos/{owner}/{repo}/pulls/{number}/labels")

def add_labels(
    self, owner: str, repo: str, number: Union[int, str], labels: List[str]
) -> Any:
    self._require(owner=owner, repo=repo, number=number, labels=labels)
    return self._post(
        f"/repos/{owner}/{repo}/pulls/{number}/labels",
        json={"labels": labels},
    )

def replace_labels(
    self, owner: str, repo: str, number: Union[int, str], labels: List[str]
) -> Any:
    self._require(owner=owner, repo=repo, number=number, labels=labels)
    return self._put(
        f"/repos/{owner}/{repo}/pulls/{number}/labels",
        json={"labels": labels},
    )

def delete_label(
    self, owner: str, repo: str, number: Union[int, str], name: str
) -> Any:
    self._require(owner=owner, repo=repo, number=number, name=name)
    return self._delete(f"/repos/{owner}/{repo}/pulls/{number}/labels/{name}")

def get_comment(self, owner: str, repo: str, comment_id: Union[int, str]) -> Any:
    self._require(owner=owner, repo=repo, comment_id=comment_id)
    return self._get(f"/repos/{owner}/{repo}/pulls/comments/{comment_id}")

def update_comment(
    self, owner: str, repo: str, comment_id: Union[int, str], body: str
) -> Any:
    self._require(owner=owner, repo=repo, comment_id=comment_id, body=body)
    return self._patch(
        f"/repos/{owner}/{repo}/pulls/comments/{comment_id}",
        json={"body": body},
    )

def delete_comment(self, owner: str, repo: str, comment_id: Union[int, str]) -> Any:
    self._require(owner=owner, repo=repo, comment_id=comment_id)
    return self._delete(f"/repos/{owner}/{repo}/pulls/comments/{comment_id}")
```

- [ ] **Step 4: Verify and commit**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest tests/test_pulls.py -q
```

Expected: pull request tests pass.

Commit:

```bash
git add gitee/resources/pulls.py tests/test_pulls.py
git commit -m "feat: add pull request workflow APIs"
```

## Task 4: Release Resource

**Files:**
- Create: `gitee/resources/releases.py`
- Modify: `gitee/resources/repositories.py`
- Test: `tests/test_repositories.py`

- [ ] **Step 1: Write failing release tests**

Add these tests to `tests/test_repositories.py`:

```python
def test_list_releases(mock_client):
    repos = Repositories(mock_client)
    repos.list_releases("owner", "repo", page=1, per_page=10)
    mock_client._get.assert_called_with(
        "/repos/owner/repo/releases",
        params={"page": 1, "per_page": 10},
    )


def test_create_release(mock_client):
    repos = Repositories(mock_client)
    repos.create_release("owner", "repo", tag_name="v1.0.0", name="One", body="notes")
    mock_client._post.assert_called_with(
        "/repos/owner/repo/releases",
        json={"tag_name": "v1.0.0", "name": "One", "body": "notes"},
    )


def test_get_release(mock_client):
    repos = Repositories(mock_client)
    repos.get_release("owner", "repo", 7)
    mock_client._get.assert_called_with("/repos/owner/repo/releases/7")


def test_update_release(mock_client):
    repos = Repositories(mock_client)
    repos.update_release("owner", "repo", 7, name="Two")
    mock_client.request.assert_called_with(
        "PATCH",
        "/repos/owner/repo/releases/7",
        params=None,
        json={"name": "Two"},
        data=None,
    )


def test_delete_release(mock_client):
    repos = Repositories(mock_client)
    repos.delete_release("owner", "repo", 7)
    mock_client.request.assert_called_with(
        "DELETE",
        "/repos/owner/repo/releases/7",
        params=None,
    )


def test_get_latest_release(mock_client):
    repos = Repositories(mock_client)
    repos.get_latest_release("owner", "repo")
    mock_client._get.assert_called_with("/repos/owner/repo/releases/latest")


def test_get_release_by_tag(mock_client):
    repos = Repositories(mock_client)
    repos.get_release_by_tag("owner", "repo", "v1.0.0")
    mock_client._get.assert_called_with("/repos/owner/repo/releases/tags/v1.0.0")


def test_list_release_attachments(mock_client):
    repos = Repositories(mock_client)
    repos.list_release_attachments("owner", "repo", 7)
    mock_client._get.assert_called_with(
        "/repos/owner/repo/releases/7/attach_files",
        params={},
    )


def test_get_release_attachment(mock_client):
    repos = Repositories(mock_client)
    repos.get_release_attachment("owner", "repo", 7, 3)
    mock_client._get.assert_called_with(
        "/repos/owner/repo/releases/7/attach_files/3"
    )


def test_delete_release_attachment(mock_client):
    repos = Repositories(mock_client)
    repos.delete_release_attachment("owner", "repo", 7, 3)
    mock_client.request.assert_called_with(
        "DELETE",
        "/repos/owner/repo/releases/7/attach_files/3",
        params=None,
    )


def test_download_release_attachment(mock_client):
    repos = Repositories(mock_client)
    repos.download_release_attachment("owner", "repo", 7, 3)
    mock_client._get.assert_called_with(
        "/repos/owner/repo/releases/7/attach_files/3/download"
    )
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest tests/test_repositories.py -q
```

Expected: fails with `AttributeError` for release methods.

- [ ] **Step 3: Implement `Releases` resource**

Create `gitee/resources/releases.py`:

```python
"""Repository release helpers."""

from typing import Any, Dict, List, Optional, Union

from gitee.resources.base import Resource


class Releases(Resource):
    """Repository release and release attachment endpoints."""

    def list(
        self,
        owner: str,
        repo: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._require(owner=owner, repo=repo)
        return self._get(
            f"/repos/{owner}/{repo}/releases",
            params=self._params(page=page, per_page=per_page),
        )

    def create(
        self,
        owner: str,
        repo: str,
        tag_name: str,
        name: Optional[str] = None,
        body: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, tag_name=tag_name)
        data = self._json(tag_name=tag_name, name=name, body=body, **kwargs)
        return self._post(f"/repos/{owner}/{repo}/releases", json=data)

    def get(self, owner: str, repo: str, release_id: Union[int, str]) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, release_id=release_id)
        return self._get(f"/repos/{owner}/{repo}/releases/{release_id}")

    def update(
        self, owner: str, repo: str, release_id: Union[int, str], **kwargs: Any
    ) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, release_id=release_id)
        return self._patch(
            f"/repos/{owner}/{repo}/releases/{release_id}",
            json=self._json(**kwargs),
        )

    def delete(self, owner: str, repo: str, release_id: Union[int, str]) -> Any:
        self._require(owner=owner, repo=repo, release_id=release_id)
        return self._delete(f"/repos/{owner}/{repo}/releases/{release_id}")

    def latest(self, owner: str, repo: str) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo)
        return self._get(f"/repos/{owner}/{repo}/releases/latest")

    def by_tag(self, owner: str, repo: str, tag: str) -> Dict[str, Any]:
        self._require(owner=owner, repo=repo, tag=tag)
        return self._get(f"/repos/{owner}/{repo}/releases/tags/{tag}")

    def list_attachments(
        self,
        owner: str,
        repo: str,
        release_id: Union[int, str],
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        self._require(owner=owner, repo=repo, release_id=release_id)
        return self._get(
            f"/repos/{owner}/{repo}/releases/{release_id}/attach_files",
            params=self._params(page=page, per_page=per_page),
        )

    def get_attachment(
        self,
        owner: str,
        repo: str,
        release_id: Union[int, str],
        attach_file_id: Union[int, str],
    ) -> Dict[str, Any]:
        self._require(
            owner=owner, repo=repo, release_id=release_id, attach_file_id=attach_file_id
        )
        return self._get(
            f"/repos/{owner}/{repo}/releases/{release_id}/attach_files/{attach_file_id}"
        )

    def delete_attachment(
        self,
        owner: str,
        repo: str,
        release_id: Union[int, str],
        attach_file_id: Union[int, str],
    ) -> Any:
        self._require(
            owner=owner, repo=repo, release_id=release_id, attach_file_id=attach_file_id
        )
        return self._delete(
            f"/repos/{owner}/{repo}/releases/{release_id}/attach_files/{attach_file_id}"
        )

    def download_attachment(
        self,
        owner: str,
        repo: str,
        release_id: Union[int, str],
        attach_file_id: Union[int, str],
    ) -> Any:
        self._require(
            owner=owner, repo=repo, release_id=release_id, attach_file_id=attach_file_id
        )
        return self._get(
            f"/repos/{owner}/{repo}/releases/{release_id}/attach_files/{attach_file_id}/download"
        )
```

- [ ] **Step 4: Delegate through `Repositories`**

In `gitee/resources/repositories.py`, import and instantiate `Releases`:

```python
from gitee.resources.releases import Releases
```

```python
self._releases = Releases(client)
```

Add public methods:

```python
def list_releases(
    self,
    owner: str,
    repo: str,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """获取仓库 Release 列表。"""
    return self._releases.list(owner, repo, page=page, per_page=per_page)

def create_release(
    self,
    owner: str,
    repo: str,
    tag_name: str,
    name: Optional[str] = None,
    body: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """创建仓库 Release。"""
    return self._releases.create(
        owner, repo, tag_name, name=name, body=body, **kwargs
    )

def get_release(self, owner: str, repo: str, release_id: Union[int, str]) -> Dict[str, Any]:
    """获取仓库 Release。"""
    return self._releases.get(owner, repo, release_id)

def update_release(
    self, owner: str, repo: str, release_id: Union[int, str], **kwargs: Any
) -> Dict[str, Any]:
    """更新仓库 Release。"""
    return self._releases.update(owner, repo, release_id, **kwargs)

def delete_release(self, owner: str, repo: str, release_id: Union[int, str]) -> Any:
    """删除仓库 Release。"""
    return self._releases.delete(owner, repo, release_id)

def get_latest_release(self, owner: str, repo: str) -> Dict[str, Any]:
    """获取仓库最新 Release。"""
    return self._releases.latest(owner, repo)

def get_release_by_tag(self, owner: str, repo: str, tag: str) -> Dict[str, Any]:
    """根据 tag 获取仓库 Release。"""
    return self._releases.by_tag(owner, repo, tag)

def list_release_attachments(
    self,
    owner: str,
    repo: str,
    release_id: Union[int, str],
    page: Optional[int] = None,
    per_page: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """获取 Release 附件列表。"""
    return self._releases.list_attachments(
        owner, repo, release_id, page=page, per_page=per_page
    )

def get_release_attachment(
    self,
    owner: str,
    repo: str,
    release_id: Union[int, str],
    attach_file_id: Union[int, str],
) -> Dict[str, Any]:
    """获取 Release 附件。"""
    return self._releases.get_attachment(owner, repo, release_id, attach_file_id)

def delete_release_attachment(
    self,
    owner: str,
    repo: str,
    release_id: Union[int, str],
    attach_file_id: Union[int, str],
) -> Any:
    """删除 Release 附件。"""
    return self._releases.delete_attachment(owner, repo, release_id, attach_file_id)

def download_release_attachment(
    self,
    owner: str,
    repo: str,
    release_id: Union[int, str],
    attach_file_id: Union[int, str],
) -> Any:
    """下载 Release 附件。"""
    return self._releases.download_attachment(owner, repo, release_id, attach_file_id)
```

- [ ] **Step 5: Verify and commit**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest tests/test_repositories.py -q
```

Expected: repository tests pass.

Commit:

```bash
git add gitee/resources/releases.py gitee/resources/repositories.py tests/test_repositories.py
git commit -m "feat: add repository release APIs"
```

## Task 5: Live Smoke Coverage

**Files:**
- Modify: `tests/test_live_gitee.py`

- [ ] **Step 1: Add opt-in live tests for read-safe new methods**

Add read-safe tests to `tests/test_live_gitee.py` using the existing
`_client_from_env()` helper:

```python
@pytest.mark.live
def test_live_public_repository_readme_and_contents_are_readable():
    client = _client_from_env()
    readme = client.repositories.get_readme("oschina", "gitee")
    assert readme

    contents = client.repositories.get_contents("oschina", "gitee")
    assert contents


@pytest.mark.live
def test_live_public_repository_compare_and_release_list_are_readable():
    client = _client_from_env()
    branches = client.repositories.list_branches("oschina", "gitee", per_page=1)
    assert branches

    branch = branches[0]["name"]
    comparison = client.repositories.compare_commits("oschina", "gitee", branch, branch)
    assert comparison

    releases = client.repositories.list_releases("oschina", "gitee", per_page=1)
    assert isinstance(releases, list)
```

- [ ] **Step 2: Add live mutation test scaffold that remains skipped without a token**

Add a test that uses `GITEE_LIVE_MUTATION_REPO` and does not create/delete remote
repositories by itself:

```python
@pytest.mark.live
def test_live_owned_repository_file_and_release_round_trip():
    target = os.environ.get("GITEE_LIVE_MUTATION_REPO")
    if not target:
        pytest.skip("GITEE_LIVE_MUTATION_REPO is required for mutation live tests")

    owner, repo = target.split("/", 1)
    client = _client_from_env()
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
```

- [ ] **Step 3: Run non-live tests and commit**

Run:

```bash
env -u GITEE_TOKEN UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest -m "not live" -q
```

Expected: all non-live tests pass and live tests are deselected.

Commit:

```bash
git add tests/test_live_gitee.py
git commit -m "test: add live smoke coverage for priority APIs"
```

## Task 6: Quality Gate And Documentation

**Files:**
- Modify: `DESIGN.md` only if it lists supported endpoint families.
- Modify: `README.md` only if it has a feature list that would become stale.

- [ ] **Step 1: Run formatting**

Run:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with black black gitee tests
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with isort isort gitee tests
```

Expected: commands complete successfully. Inspect `git diff` and ensure only formatting changes related to touched files are present.

- [ ] **Step 2: Run full non-live verification**

Run:

```bash
env -u GITEE_TOKEN UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest -m "not live" -q
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with black black --check gitee tests
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with isort isort --check-only gitee tests
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with mypy --with requests --with pydantic mypy gitee
```

Expected: pytest, black, isort, and mypy pass.

- [ ] **Step 3: Update docs if needed**

If `README.md` or `DESIGN.md` contains an endpoint coverage list, update it with
these bullets:

```markdown
- Repository content APIs: README, contents, create/update/delete file, compare, blame, and multi-file commits.
- Governance APIs: branch creation/protection and collaborator permission reads.
- Pull request workflow APIs: merge status, review/test assignment, linked issues, labels, and comment mutation.
- Release APIs: release CRUD plus attachment list/get/delete/download.
```

If neither file has such a list, skip documentation changes and record that no
user-facing feature list exists.

- [ ] **Step 4: Commit quality and docs changes**

Run:

```bash
git status --short
```

If formatting or docs changed, commit them:

```bash
git add gitee tests README.md DESIGN.md
git commit -m "docs: update priority api coverage notes"
```

If no files changed, do not create an empty commit.

## Final Verification

- [ ] **Run complete non-live verification**

```bash
env -u GITEE_TOKEN UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest -m "not live" -q
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with black black --check gitee tests
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with isort isort --check-only gitee tests
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with mypy --with requests --with pydantic mypy gitee
```

Expected: all commands pass.

- [ ] **Optional live verification**

Run read-only live tests when `GITEE_TOKEN` is available:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest -m live -q -rs
```

Run mutation live tests only when `GITEE_LIVE_MUTATION_REPO=owner/repo` points to
a disposable repository owned by the token:

```bash
GITEE_LIVE_MUTATION_REPO=owner/repo env UV_CACHE_DIR=/tmp/uv-cache uv run --no-project --with pytest --with requests --with pydantic pytest tests/test_live_gitee.py::test_live_owned_repository_file_and_release_round_trip -q -rs
```

Expected: read-only live tests pass against public repositories; mutation test
passes only against the explicitly provided disposable repository.

## Self-Review Notes

- Spec coverage: content APIs are Task 1, branch/collaborator governance is Task 2, PR workflow is Task 3, release publishing is Task 4, live/non-live verification is Tasks 5-6.
- Low-priority metadata and social endpoints remain out of scope.
- Attachment upload is intentionally excluded because the spec allows deferring it until multipart client support is designed.
