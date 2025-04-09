"""Gitee API SDK for Python.

A comprehensive Python SDK for the Gitee API, providing a clean and easy-to-use
interface for interacting with Gitee's platform.

Example:
    >>> from gitee import GiteeClient
    >>> client = GiteeClient(token="your_access_token")
    >>> repos = client.repositories.list()
    >>> for repo in repos:
    ...     print(f"{repo['full_name']}: {repo['description']}")
"""

from gitee.client import GiteeClient
from gitee.exceptions import (
    GiteeException,
    APIError,
    AuthenticationError,
    RateLimitExceeded,
)

__version__ = "0.1.0"
__all__ = ["GiteeClient", "GiteeException", "APIError", "AuthenticationError", "RateLimitExceeded"]