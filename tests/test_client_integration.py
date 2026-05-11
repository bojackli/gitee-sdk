import pytest
import requests

from gitee.client import GiteeClient
from gitee.exceptions import APIError, RateLimitExceeded
from gitee.resources.base import PaginatedList


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", headers=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.headers = headers or {}
        self.content = text.encode("utf-8") if text else b"x"

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            error = requests.exceptions.HTTPError("HTTP error")
            error.response = self
            raise error


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.headers = {}
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)

    def close(self):
        pass


def test_client_parses_json_response():
    client = GiteeClient()
    client.session = FakeSession([FakeResponse(payload={"id": 1})])
    assert client.request("GET", "/user") == {"id": 1}
    assert client.session.calls[0]["url"] == "https://gitee.com/api/v5/user"


def test_client_returns_text_for_non_json_response():
    client = GiteeClient()
    client.session = FakeSession([FakeResponse(payload=ValueError(), text="raw")])
    assert client.request("GET", "/raw") == "raw"


def test_client_returns_none_for_204_response():
    response = FakeResponse(status_code=204, payload=None, text="")
    response.content = b""
    client = GiteeClient()
    client.session = FakeSession([response])
    assert client.request("DELETE", "/resource") is None


def test_client_maps_api_error():
    client = GiteeClient()
    client.session = FakeSession(
        [FakeResponse(status_code=404, payload={"message": "Not found"})]
    )
    with pytest.raises(APIError) as exc:
        client.request("GET", "/missing")
    assert exc.value.status_code == 404
    assert exc.value.message == "Not found"


def test_client_raises_rate_limit_after_successful_response():
    client = GiteeClient()
    client.session = FakeSession(
        [
            FakeResponse(
                payload={"ok": True},
                headers={
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": "123",
                },
            )
        ]
    )
    with pytest.raises(RateLimitExceeded) as exc:
        client.request("GET", "/limited")
    assert exc.value.reset_time == "123"


def test_paginated_list_fetches_until_empty_page():
    client = GiteeClient()
    client.session = FakeSession(
        [
            FakeResponse(payload=[{"id": 1}, {"id": 2}]),
            FakeResponse(payload=[]),
        ]
    )
    paginated = PaginatedList(client, "/items", params={"state": "open"})
    assert paginated.all() == [{"id": 1}, {"id": 2}]
    assert client.session.calls[0]["params"] == {
        "state": "open",
        "page": 1,
        "per_page": 20,
    }
    assert client.session.calls[1]["params"] == {
        "state": "open",
        "page": 2,
        "per_page": 20,
    }
