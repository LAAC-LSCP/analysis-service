from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
import requests

from src.core.types import TaskStatus
from src.service.http_client import HTTPClient

_TASK_ID = UUID("c611e347-2c08-4909-b174-0e76a678ce57")


def _make_http_client(retry_time_s: int = 10) -> HTTPClient:
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
            retry_time_s=retry_time_s,
        )


def _response_raising(status_code: int) -> MagicMock:
    response = MagicMock()
    response.raise_for_status.side_effect = requests.HTTPError(
        response=MagicMock(status_code=status_code)
    )
    return response


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


def test_put_task_retries_on_server_error_then_succeeds():
    client = _make_http_client(retry_time_s=5)

    success_response = MagicMock()
    success_response.raise_for_status.return_value = None

    with patch("src.service.http_client.requests.put") as mock_put:
        mock_put.side_effect = [_response_raising(500), success_response]
        client.put_task(_TASK_ID, payload={"status": TaskStatus.COMPLETED})

    assert mock_put.call_count == 2


def test_put_task_does_not_retry_on_client_error():
    client = _make_http_client(retry_time_s=5)

    with patch("src.service.http_client.requests.put") as mock_put:
        mock_put.return_value = _response_raising(400)

        with pytest.raises(RuntimeError):
            client.put_task(_TASK_ID, payload={"status": TaskStatus.COMPLETED})

    assert mock_put.call_count == 1


def test_put_task_gives_up_after_retry_budget_exhausted():
    client = _make_http_client(retry_time_s=1)

    with patch("src.service.http_client.requests.put") as mock_put:
        mock_put.return_value = _response_raising(503)

        with pytest.raises(RuntimeError):
            client.put_task(_TASK_ID, payload={"status": TaskStatus.COMPLETED})

    assert mock_put.call_count >= 1
