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
