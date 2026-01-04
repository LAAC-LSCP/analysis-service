"""
"Contract tests" against the real Echolalia API

Also "verifying fakes", that is, our FakeHTTPClient class
"""

import os

import pytest

from src.service.http_client import HTTPClient

BASE_URL = os.environ.get("ECHOLALIA_BASE_URL")
CLIENT_ID = os.environ.get("ECHOLALIA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ECHOLALIA_CLIENT_SECRET")


@pytest.mark.skipif(
    not all([BASE_URL, CLIENT_ID, CLIENT_SECRET]),
    reason="Requires environment variables: \
ECHOLALIA_BASE_URL, ECHOLALIA_CLIENT_ID, ECHOLALIA_CLIENT_SECRET",
)
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
