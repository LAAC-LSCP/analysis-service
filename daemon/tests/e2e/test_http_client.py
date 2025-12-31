"""
"Contract tests" against the real Echolalia API

Also "verifying fakes", that is, our FakeHTTPClient class
"""

import os

import pytest

from src.service.http_client import HTTPClient

BASE_URL = os.getenv("ECHOLALIA_BASE_URL")
CLIENT_ID = os.getenv("ECHOLALIA_CLIENT_ID")
CLIENT_SECRET = os.getenv("ECHOLALIA_CLIENT_SECRET")


def test_env_variables_are_there():
    assert BASE_URL is not None
    assert CLIENT_ID is not None
    assert CLIENT_SECRET is not None


def test_get_all_tasks():
    http_client = HTTPClient(
        base_url=BASE_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
    fake_http_client = HTTPClient(
        base_url=BASE_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )

    try:
        http_client.get_all_tasks()
        fake_http_client.get_all_tasks()
    except Exception as e:
        pytest.fail(f"get_all_tasks() raised an exception: {e}")
