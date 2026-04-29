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
