import pytest
import requests
from analysis_service_core.src.config import Config, EnvVar


@pytest.fixture(scope="session", autouse=True)
def config() -> Config:
    env_vars = {
        EnvVar("EXPECTED_CLIENT_ID", str),
        EnvVar("EXPECTED_CLIENT_SECRET", str),
        EnvVar("BASE_URL", str),
    }

    return Config(env_vars, check_required=False)


@pytest.fixture(scope="session", autouse=True)
def authentication_token(config: Config) -> str:
    login_url = f"{config.get("BASE_URL")}/api/auth/login-service"
    login_payload = {
        "client_id": config.get("EXPECTED_CLIENT_ID"),
        "client_secret": config.get("EXPECTED_CLIENT_SECRET"),
    }
    login_resp = requests.post(login_url, json=login_payload)
    token = login_resp.json()["access_token"]

    return token
