from http import HTTPStatus
from typing import Mapping, Optional, Tuple
from uuid import UUID
import time

import requests
from tenacity import retry, stop_after_delay, wait_fixed

import src.core.elsi_api as external_api

Headers = Mapping[str, str]


class HTTPClient:
    """
    The HTTPClient calls the ELSI endpoint to get tasks. It also
    allows updating the server's task statuses
    """

    _retry_time_s: int = 10
    _timeout_s: int

    _base_url: str
    _access_token: str

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        timeout_s: Optional[int] = 10,
        retry_time_s: Optional[int] = 10,
    ):
        self._timeout_s = timeout_s or 10
        self._retry_time_s = retry_time_s or 10

        self._base_url = base_url
        self._access_token, self._access_token_expiration, _ = self._get_access_token(client_id, client_secret)

        # set the renew window to 1min before expiration
        self._access_token_expiration = time.time() + self._access_token_expiration -60

        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def headers(self) -> Headers:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "accept": "application/json",
        }

    @retry(stop=stop_after_delay(10), wait=wait_fixed(1), reraise=True)
    def _get_access_token(
        self, client_id: str, client_secret: str
    ) -> Tuple[str, int, str]:
        uri: str = self._base_url + "/auth/login-service"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
        }
        headers: Headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        response: requests.Response = requests.post(
            uri, json=payload, timeout=self._timeout_s, headers=headers
        )
        response.raise_for_status()

        response_json: external_api.AuthResponse = response.json()

        return (
            response_json["access_token"],
            response_json["expires_in"],
            response_json["token_type"],
        )

    def _check_access_token(
        self,
    ) -> None:
        if time.time() > self._access_token_expiration:
            self._access_token, self._access_token_expiration, _ = self._get_access_token(self._client_id, self._client_secret)

            # set the renew window to 1min before expiration
            self._access_token_expiration = time.time() + self._access_token_expiration -60


    def get_all_tasks(self) -> external_api.Tasks:
        uri: str = self._base_url + "/analytics/services/tasks"

        try:
            self._check_access_token()
            response = requests.get(uri, headers=self.headers, timeout=self._timeout_s)
            response.raise_for_status()
            data = response.json()

            return {external_api.Task.from_dict(task) for task in data}
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Failed to fetch tasks from {self._base_url}: {exc}"
            ) from exc

    def get_task_by_id(self, id: UUID) -> Optional[external_api.Task]:
        uri: str = self._base_url + f"/analytics/services/tasks/{str(id)}"

        try:
            self._check_access_token()
            response = requests.get(uri, headers=self.headers, timeout=self._timeout_s)
            response.raise_for_status()
            data = response.json()

            return external_api.Task.from_dict(data)
        except requests.RequestException as exc:
            if exc.response and exc.response.status_code == HTTPStatus.NOT_FOUND:
                return None

            raise RuntimeError(f"Failed to fetch task with UUID {id} from \
                {self._base_url}: {exc}") from exc

    def put_task(self, task_id: UUID, payload: external_api.PutPayload) -> None:
        uri: str = self._base_url + f"/analytics/services/tasks/{str(task_id)}"

        body: dict = {"status": payload["status"].upper()}
        if "estimated_duration" in payload:
            body["estimated_duration"] = payload["estimated_duration"]
        if "progress" in payload:
            body["progress"] = payload["progress"]

        try:
            self._check_access_token()
            response = requests.put(
                uri,
                json=body,
                headers=self.headers,
                timeout=self._timeout_s,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to post task: {exc}") from exc
