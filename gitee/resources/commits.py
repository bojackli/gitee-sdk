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
