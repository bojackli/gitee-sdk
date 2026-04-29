# SDK Architecture Boundary Design

## Context

The current SDK uses a reasonable thin-client structure: `GiteeClient` owns HTTP session behavior, authentication, response parsing, and error mapping; `Resource` provides shared request helpers; concrete resource classes map Python method calls to Gitee API paths, query parameters, and request bodies.

The main architectural risk is not the direction, but boundary drift. `repositories.py` already mixes repository CRUD, branches, commits, collaborators, forks, and raw file access. `PaginatedList` exists but is not consistently exposed by list methods. `DESIGN.md` also describes modules such as `git_data.py` that no longer match the implementation.

## Goals

- Preserve the public SDK style, including calls such as `client.repositories.get(...)`.
- Make resource modules easier to extend without large files accumulating unrelated API areas.
- Turn pagination into an explicit, documented capability.
- Keep the SDK as a thin API wrapper rather than introducing heavy request/response models.
- Add real Gitee API feedback through controlled live tests.

## Non-Goals

- Do not redesign the whole SDK around generated OpenAPI clients.
- Do not break existing public method names during the first refactor.
- Do not introduce Pydantic request models for every endpoint.
- Do not make live API tests part of the default local test command.

## Target Boundaries

`GiteeClient` should only handle transport-level concerns: base URL handling, session headers, authentication, request dispatch, response parsing, rate-limit checks, and exception mapping.

`Resource` should hold cross-resource helpers: HTTP verb wrappers, required-parameter validation shortcuts, `None` filtering, and pagination construction.

Concrete resources should only translate SDK method arguments into API paths, query params, and request bodies. They should not duplicate transport behavior or know `requests` internals.

## Resource Split Strategy

The first split target is `repositories.py`, because it contains several independently named subdomains. Keep the external API stable while moving internals toward smaller modules:

```text
gitee/resources/repositories.py      # repository CRUD, repository list, forks, raw file access
gitee/resources/branches.py          # branch operations
gitee/resources/commits.py           # commit operations
gitee/resources/collaborators.py     # collaborator operations
```

In the first phase, `Repositories` can compose these internal helpers and continue exposing existing methods such as `list_branches`, `list_commits`, and `add_collaborator`. Do not expose `client.branches` or `client.commits` until there is a deliberate public API migration plan.

`issues.py` and `pulls.py` can remain intact for now. Revisit them only if comments, labels, reviews, or other subdomains grow enough to justify separate modules.

## Pagination Design

Do not silently change existing list methods from `list` returns to paginated iterator returns. Preserve current behavior:

```python
client.repositories.list("owner")
```

Add explicit paginated variants:

```python
client.repositories.list_paginated("owner")
```

This keeps return types predictable. `list_paginated` should construct a `PaginatedList` through a shared `Resource` helper so pagination behavior is consistent across resource classes.

## Parameter Handling

Keep `filter_none_values` and `validate_required_params`, but reduce call-site repetition by adding small `Resource` helpers such as `_params(...)`, `_json(...)`, and `_require(...)`. These helpers should remain simple wrappers around dictionaries and validation, not schema systems.

## Testing Strategy

Use three test layers:

```text
unit tests
  -> mock client; verify HTTP method, path, params, and JSON body

integration tests
  -> mock HTTP responses; verify client response parsing, errors, and pagination

live tests
  -> real Gitee API; verify a small stable set of read-only endpoints
```

Live tests should be marked separately, for example `pytest -m live`, and should read credentials from environment variables such as `GITEE_TOKEN`. They should cover stable, low-risk, read-only behavior: current user lookup, public repository details, and public repository branch or commit listing. Write-operation live tests require a dedicated test repository and cleanup logic before they are added.

Default local and PR test runs should continue to use unit and integration tests. CI can run live tests through a manual or scheduled workflow to provide real API feedback without making every contribution depend on network stability.

## Documentation Updates

Update `DESIGN.md` after implementation so it reflects actual modules and the new pagination/testing approach. Remove or revise stale references such as `git_data.py`.

## Implementation Order

1. Add characterization tests around existing repository methods.
2. Add `Resource` helpers for params, JSON bodies, required params, and paginated construction.
3. Introduce internal modules for branches, commits, and collaborators.
4. Rewire `Repositories` to delegate internally while preserving public method names.
5. Add explicit `list_paginated` methods where useful.
6. Add integration tests for pagination and client error handling.
7. Add marked live tests for stable read-only Gitee API calls.
8. Update `DESIGN.md` to match the final structure.
