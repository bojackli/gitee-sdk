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
