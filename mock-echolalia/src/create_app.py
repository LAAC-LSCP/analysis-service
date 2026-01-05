import secrets

from flask import Flask, jsonify, request
from flask_httpauth import HTTPTokenAuth

from src.app_types import Database, FlaskConfig


def create_app(
    db: Database,
    expected_client_id: str | None = None,
    expected_client_secret: str | None = None,
) -> Flask:
    app = Flask(__name__)
    app.config[FlaskConfig.TASK_DB] = db
    app.config[FlaskConfig.TOKENS] = set()
    auth = HTTPTokenAuth(scheme="Bearer")

    @app.route("/api/auth/login-service", methods=["POST"])
    def login_service():
        data = request.json

        if (
            data.get("client_id") == expected_client_id
            and data.get("client_secret") == expected_client_secret
        ):
            token = secrets.token_urlsafe(32)
            app.config[FlaskConfig.TOKENS].add(token)

            return jsonify(
                {
                    "access_token": token,
                    "expires_in": 3600,
                    "token_type": "bearer",
                }
            )

        return jsonify({"error": "Unauthorized"}), 401

    @auth.verify_token
    def verify_token(token):
        return token in app.config[FlaskConfig.TOKENS]

    @app.route("/api/analytics/services/tasks", methods=["GET"])
    @auth.login_required
    def get_tasks():
        print("Received request to get all tasks")
        db: Database = app.config[FlaskConfig.TASK_DB]
        tasks = db.tasks

        task_dict = [task.model_dump() for task in tasks]

        return jsonify(task_dict)

    @app.route("/api/analytics/services/tasks/<task_id>", methods=["GET"])
    @auth.login_required
    def get_task(task_id):
        print(f"Received request to get task with id '{task_id}'")
        db: Database = app.config[FlaskConfig.TASK_DB]

        task = next((t for t in db.tasks if str(t.task_uid) == task_id), None)

        if task is None:
            return jsonify({"error": "Task not found"}), 404

        return jsonify(task.model_dump())

    @app.route("/api/analytics/services/tasks/<task_id>", methods=["PUT"])
    @auth.login_required
    def update_task(task_id):
        print(
            f"Received request to update task with id '{task_id}' and \
data '{request.json}'"
        )
        db: Database = app.config[FlaskConfig.TASK_DB]
        data = request.json

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        task = next((t for t in db.tasks if str(t.task_uid) == task_id), None)

        if task is None:
            return jsonify({"error": "Task not found"}), 404

        if "status" in data:
            task.status_label = data["status"].lower()

        if "estimated_duration" in data:
            task.estimated_duration = data["estimated_duration"]

        return jsonify(task.model_dump())

    return app
