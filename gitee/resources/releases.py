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
