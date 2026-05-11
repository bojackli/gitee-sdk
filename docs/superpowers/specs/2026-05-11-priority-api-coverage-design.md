# Priority API Coverage Design

## Status

Awaiting written spec review.

## Context

The SDK already covers the basic repository, issue, pull request, label,
milestone, webhook, user, and gist flows, plus a small internal resource split
for branches, commits, and collaborators. The next gap is not broad Swagger
parity. The useful target is API coverage that supports real repository
automation: create code changes, manage branches and collaborators, drive pull
requests, and publish releases.

Official reference: `https://gitee.com/sdk/typescript-sdk-v5/raw/main/openapi-spec.json`.

## Goals

- Add high-value missing endpoints before low-value display metadata.
- Preserve the existing public API shape, especially `client.repositories` and
  `client.pulls`.
- Keep modules small by adding internal resources instead of growing
  `repositories.py` indefinitely.
- Provide tests that verify concrete request paths, methods, query params, and
  JSON bodies without depending on live network access by default.

## Non-Goals

The first implementation will not cover `languages`, stargazers, subscribers,
events, notifications, Pages, Baidu statistic keys, traffic data, or Gitee Go.
Those endpoints can be added later if a concrete workflow needs them.

## Priority Coverage

### Repository Content And Commit Automation

Add repository methods for README/content/file operations and comparison:

- `get_readme(owner, repo, ref=None)`
- `get_contents(owner, repo, path="", ref=None)`
- `create_file(owner, repo, path, content, message, branch=None, **kwargs)`
- `update_file(owner, repo, path, content, message, sha, branch=None, **kwargs)`
- `delete_file(owner, repo, path, message, sha, branch=None, **kwargs)`
- `create_commit(owner, repo, files, message, branch=None, **kwargs)`
- `compare_commits(owner, repo, base, head)`
- `get_blame(owner, repo, path, ref=None)`

These map to the official `/contents`, `/commits`, `/compare`, `/readme`, and
`/blame` repository endpoints. File mutation methods should accept `**kwargs`
for official optional fields while keeping required fields explicit.

### Branch And Collaborator Governance

Extend branch and collaborator support with:

- `create_branch(owner, repo, refs, branch_name)`
- `protect_branch(owner, repo, branch, **kwargs)`
- `unprotect_branch(owner, repo, branch)`
- `create_branch_protection_rule(owner, repo, wildcard, **kwargs)`
- `update_branch_protection_rule(owner, repo, wildcard, **kwargs)`
- `delete_branch_protection_rule(owner, repo, wildcard)`
- `is_collaborator(owner, repo, username)`
- `get_collaborator_permission(owner, repo, username)`

Branch protection payloads should pass through official fields via `**kwargs`
because Gitee exposes several policy switches. The SDK should validate path
parameters and leave policy validation to the API.

### Pull Request Workflow Completion

Extend `PullRequests` with missing workflow operations:

- `is_merged(owner, repo, number)`
- `review(owner, repo, number, event, body=None, **kwargs)`
- `test(owner, repo, number, event, body=None, **kwargs)`
- `assign_reviewers(owner, repo, number, assignees)`
- `unassign_reviewers(owner, repo, number, assignees)`
- `reset_reviewer_state(owner, repo, number, assignees)`
- `assign_testers(owner, repo, number, testers)`
- `unassign_testers(owner, repo, number, testers)`
- `reset_tester_state(owner, repo, number, testers)`
- `list_issues(owner, repo, number)`
- PR label helpers mirroring issue label operations.
- `get_comment(owner, repo, comment_id)`, `update_comment(...)`,
  `delete_comment(...)`

The method names should describe SDK intent rather than repeat Swagger names.
Reviewer/tester payloads should accept both a list and official keyword fields
where needed.

### Release Publishing

Add a release-focused internal resource surfaced through `client.repositories`:

- `list_releases(owner, repo, page=None, per_page=None)`
- `create_release(owner, repo, tag_name, name=None, body=None, **kwargs)`
- `get_release(owner, repo, release_id)`
- `update_release(owner, repo, release_id, **kwargs)`
- `delete_release(owner, repo, release_id)`
- `get_latest_release(owner, repo)`
- `get_release_by_tag(owner, repo, tag)`
- Attachment list/get/delete/download methods.

Attachment upload can be implemented after basic Release CRUD if multipart
handling requires client-level support.

## Architecture

Keep the public surface stable:

- `Repositories` delegates to new internal resources such as `Contents`,
  `Releases`, and expanded `Branches`/`Collaborators`.
- `PullRequests` owns PR workflow methods directly unless the file becomes too
  large, at which point a private helper resource can be introduced.
- New code should use `Resource._require`, `_params`, and `_json` rather than
  the older utility helpers where practical.

## Testing Strategy

Unit tests are required for every new method and should assert exact endpoint,
HTTP method, params, and JSON payload. Live tests remain opt-in under the
existing `live` marker. The live scope for this feature should focus on a
temporary repository covering file create/update/delete, branch creation, PR
read operations, merge status read, and Release create/delete. Permission-heavy
features such as collaborator writes, branch protection, and attachment upload
can stay unit-tested until a stable live fixture exists.

## Acceptance Criteria

- High-priority endpoints above are exposed with clear SDK method names.
- Low-priority metadata/social/platform endpoints remain out of scope.
- New methods follow existing resource style and type hints.
- Mock tests pass without network access.
- Existing non-live tests continue to pass.
