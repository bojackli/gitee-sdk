# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python SDK for the Gitee API. The importable package lives in `gitee/`: core client behavior is in `client.py`, authentication/configuration helpers are in `auth.py` and `config.py`, and endpoint groups are implemented in `gitee/resources/`. Shared resource behavior belongs in `gitee/resources/base.py`; add new API groups as separate resource modules and export them through the package where appropriate. Tests live in `tests/` and mirror resource areas, for example `tests/test_repositories.py` and `tests/test_pulls.py`. Usage examples belong in `examples/`. Packaging metadata is split between `pyproject.toml` and `setup.py`.

## Build, Test, and Development Commands

Install the project with development tools:

```bash
uv pip install -e ".[dev]"
```

Run the full test suite:

```bash
pytest
```

Run coverage when changing SDK behavior:

```bash
pytest --cov=gitee
```

Format and sort imports before submitting:

```bash
black gitee tests examples
isort gitee tests examples
```

Build distribution artifacts locally:

```bash
python setup.py sdist bdist_wheel
```

## Coding Style & Naming Conventions

Target Python 3.8+. Use 4-space indentation, type hints for public methods, and concise docstrings or comments only where they clarify behavior. Black is configured with an 88-character line length, and isort uses the Black profile. Resource classes should use clear API-area names such as `Repositories`, `Issues`, and `Pulls`; test methods should use `test_<behavior>` names.

## Testing Guidelines

Tests use `pytest` with `unittest.mock.Mock` for client calls. Prefer fast unit tests that assert the generated HTTP method, path, parameters, and JSON body rather than making live Gitee requests. Add or update tests in `tests/` whenever changing a resource method, client behavior, pagination, or error handling.

## Commit & Pull Request Guidelines

Recent history uses short imperative or scoped messages, including examples like `ci: 更新发布工作流的触发条件`, `refactor(repositories): ...`, and automated `Bump version to ... [skip ci]`. Keep commits focused and use a scope when it helps. Pull requests should describe the API surface changed, list test commands run, link related issues, and include examples or screenshots only when changing documentation or user-facing examples.

## Security & Configuration Tips

Do not commit access tokens or real credentials. Tests should mock network interactions. Publishing is handled by GitHub Actions using repository secrets for TestPyPI and PyPI; avoid manual version edits unless preparing a release intentionally.
