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
