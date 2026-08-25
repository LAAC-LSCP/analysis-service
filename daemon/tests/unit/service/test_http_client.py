from unittest.mock import patch
from uuid import UUID

from src.core.types import TaskStatus
from src.service.http_client import HTTPClient

_TASK_ID = UUID("c611e347-2c08-4909-b174-0e76a678ce57")


def _make_http_client() -> HTTPClient:
    with patch("src.service.http_client.requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "access_token": "token",
            "expires_in": 3600,
            "token_type": "bearer",
        }
        mock_post.return_value.raise_for_status.return_value = None
        return HTTPClient(
            base_url="http://elsi.test",
            client_id="id",
            client_secret="secret",
        )


def test_put_task_sends_only_status_by_default():
    client = _make_http_client()

    with patch("src.service.http_client.requests.put") as mock_put:
        mock_put.return_value.raise_for_status.return_value = None
        client.put_task(_TASK_ID, payload={"status": TaskStatus.RUNNING})

    assert mock_put.call_args.kwargs["json"] == {"status": "RUNNING"}


def test_put_task_includes_progress_without_estimated_duration():
    client = _make_http_client()

    with patch("src.service.http_client.requests.put") as mock_put:
        mock_put.return_value.raise_for_status.return_value = None
        client.put_task(
            _TASK_ID, payload={"status": TaskStatus.RUNNING, "progress": 0.42}
        )

    assert mock_put.call_args.kwargs["json"] == {
        "status": "RUNNING",
        "progress": 0.42,
    }


def test_put_task_includes_estimated_duration_when_present():
    client = _make_http_client()

    with patch("src.service.http_client.requests.put") as mock_put:
        mock_put.return_value.raise_for_status.return_value = None
        client.put_task(
            _TASK_ID,
            payload={"status": TaskStatus.COMPLETED, "estimated_duration": 0},
        )

    assert mock_put.call_args.kwargs["json"] == {
        "status": "COMPLETED",
        "estimated_duration": 0,
    }
