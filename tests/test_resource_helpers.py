from unittest.mock import Mock

import pytest

from gitee.exceptions import ValidationError
from gitee.resources.base import PaginatedList, Resource


class TestResourceHelpers:
    def test_require_accepts_present_values(self):
        resource = Resource(Mock())
        resource._require(owner="owner", repo="repo")

    def test_require_rejects_none_values(self):
        resource = Resource(Mock())
        with pytest.raises(ValidationError, match="owner"):
            resource._require(owner=None, repo="repo")

    def test_params_filters_none_values(self):
        resource = Resource(Mock())
        assert resource._params(state="open", page=None, per_page=20) == {
            "state": "open",
            "per_page": 20,
        }

    def test_json_filters_none_values(self):
        resource = Resource(Mock())
        assert resource._json(title="Issue", body=None, labels=["bug"]) == {
            "title": "Issue",
            "labels": ["bug"],
        }

    def test_paginated_builds_paginated_list(self):
        client = Mock()
        resource = Resource(client)
        paginated = resource._paginated(
            "/repos/owner/repo/commits",
            params={"sha": "main"},
            item_key="commits",
        )
        assert isinstance(paginated, PaginatedList)
        assert paginated.client is client
        assert paginated.url == "/repos/owner/repo/commits"
        assert paginated.params == {"sha": "main"}
        assert paginated.item_key == "commits"

    def test_paginated_list_uses_configured_per_page_when_iterating(self):
        client = Mock()
        client.request.side_effect = [[{"id": 1}], []]

        paginated = PaginatedList(
            client,
            "/repos/owner/repo/branches",
            params={"per_page": 100},
        )

        assert paginated.all() == [{"id": 1}]
        assert client.request.call_args_list[0].kwargs["params"] == {
            "per_page": 100,
            "page": 1,
        }
        assert client.request.call_args_list[1].kwargs["params"] == {
            "per_page": 100,
            "page": 2,
        }
