from typing import Generator, List, Tuple
from uuid import UUID

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.create_app import create_app
from src.types import Database, FlaskConfig, Task


@pytest.fixture
def client_and_app(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[Tuple[FlaskClient, Flask]]:
    db = Database(
        tasks=[
            Task(
                uuid=UUID("ecdd43fc-501f-453a-bb31-78aee95197c5"),
                status="RUNNING",
                estimated_duration=3,
            )
        ]
    )
    app = create_app(db, "test_id", "test_secret")
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client, app


def test_auth_and_tasks(client_and_app: Tuple[FlaskClient, Flask]):
    client, app = client_and_app
    resp = client.post(
        "/api/auth/login-service",
        json={"client_id": "test_id", "client_secret": "test_secret"},
    )
    assert resp.status_code == 200
    token = resp.get_json()["access_token"]

    # 2. Call /tasks with the token
    resp = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    tasks: List[Task] = app.config[FlaskConfig.TASK_DB].tasks

    assert tasks == [Task(**task) for task in resp.get_json()]
