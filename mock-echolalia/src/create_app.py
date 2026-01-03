import secrets

from flask import Flask, jsonify, request
from flask_httpauth import HTTPTokenAuth

from src.types import Database, FlaskConfig


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

    @app.route("/tasks", methods=["GET"])
    @auth.login_required
    def show_tasks():
        db: Database = app.config[FlaskConfig.TASK_DB]
        tasks = db.tasks

        task_dict = [task.dict() for task in tasks]

        return jsonify(task_dict)

    return app
