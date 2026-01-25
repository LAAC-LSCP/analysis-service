from typing import Generator, List, Tuple
from uuid import UUID

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.app_types import Database, FlaskConfig, Task
from src.create_app import create_app


@pytest.fixture(scope="function")
def client_and_app() -> Generator[Tuple[FlaskClient, Flask, str]]:
    db = Database(
        tasks=[  # TODO: add factory
            Task(
                task_uid=UUID("ecdd43fc-501f-453a-bb31-78aee95197c5"),
                model_name="vtc",
                status_label="running",
                user_uid=UUID("b076a352-fee1-44a4-84ff-608f57b98215"),
                dataset_name="test-dataset",
                dataset_uid_label=("test-dataset-\
93f291bb-a6c1-42a4-8ed2-378df27eee0e"),
                created="2025-12-18T12:50:45.705711+01:00",
                modified="2025-12-18T12:50:45.705711+01:00",
                estimated_duration=3,
            ),
            Task(
                task_uid=UUID("c4b84d26-ac68-43de-aa5c-f166e7f75c50"),
                model_name="vtc",
                status_label="pending",
                user_uid=UUID("f15feba5-0df0-4936-841c-de4525efa996"),
                dataset_name="another-test-dataset",
                dataset_uid_label="another-test-dataset-\
b8cef380-0210-467c-970b-b7254a971cff",
                created="2025-12-18T12:50:45.705711+01:00",
                modified="2025-12-18T12:50:45.705711+01:00",
                estimated_duration=3,
            ),
        ]
    )
    app = create_app(db, "test_id", "test_secret")
    app.config["TESTING"] = True

    client = app.test_client()

    resp = client.post(
        "/api/auth/login-service",
        json={"client_id": "test_id", "client_secret": "test_secret"},
    )
    assert resp.status_code == 200
    token = resp.get_json()["access_token"]

    yield client, app, token


def test_get_tasks(client_and_app: Tuple[FlaskClient, Flask, str]):
    client, app, token = client_and_app

    resp = client.get(
        "/api/analytics/services/tasks",
        headers={"Authorization": f"Bearer \
{token}"},
    )
    assert resp.status_code == 200

    tasks: List[Task] = app.config[FlaskConfig.TASK_DB].tasks

    assert tasks == [Task(**task) for task in resp.get_json()]


def test_get_task(client_and_app: Tuple[FlaskClient, Flask, str]):
    client, app, token = client_and_app

    resp = client.get(
        "/api/analytics/services/tasks/ecdd43fc-501f-453a-bb31-78aee95197c5",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    resp_task = Task(**resp.get_json())

    tasks: List[Task] = app.config[FlaskConfig.TASK_DB].tasks

    assert resp_task in tasks


def test_post_task(client_and_app: Tuple[FlaskClient, Flask, str]):
    client, app, token = client_and_app

    tasks: List[Task] = app.config[FlaskConfig.TASK_DB].tasks

    my_pending_task: Task | None = next(
        (
            t
            for t in tasks
            if t.task_uid
            == UUID(
                "c4b84d26-ac68-43de-aa5c-f166e7f75c50",
            )
        ),
        None,
    )

    assert my_pending_task is not None

    resp = client.put(
        "/api/analytics/services/tasks/c4b84d26-ac68-43de-aa5c-f166e7f75c50",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "status": "COMPLETED",
            "estimated_duation": 5,
        },
    )
    assert resp.status_code == 200

    my_completed_task: Task | None = next(
        (
            t
            for t in tasks
            if t.task_uid
            == UUID(
                "c4b84d26-ac68-43de-aa5c-f166e7f75c50",
            )
        ),
        None,
    )

    assert my_completed_task is not None
    assert my_completed_task.status_label == "completed"
