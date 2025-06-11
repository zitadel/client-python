import json
from typing import Any, Dict

import pytest
import urllib3

import zitadel_client as zitadel
from spec.base_spec import docker_compose as docker_compose
from zitadel_client.exceptions import ZitadelError


class TestUseClientCredentialsSpec:
    """
    SettingsService Integration Tests (Client Credentials)

    This suite verifies the Zitadel SettingsService API's general settings
    endpoint works when authenticating via Client Credentials:

     1. Retrieve general settings successfully with valid credentials
     2. Expect an ApiException when using invalid credentials

    Each test instantiates a new client to ensure a clean, stateless call.
    """

    @staticmethod
    def generate_user_secret(token: str, login_name: str = "api-user") -> Dict[str, str]:
        http = urllib3.PoolManager()

        user_id_response = http.request(
            "GET",
            "http://localhost:8099/management/v1/global/users/_by_login_name",
            fields={"loginName": login_name},
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )

        if user_id_response.status < 400:
            user_response_map: Dict[str, Any] = json.loads(user_id_response.data.decode("utf-8"))
            user_payload: Any = user_response_map.get("user")
            user_id: Any = user_payload.get("id") if isinstance(user_payload, dict) else None

            if isinstance(user_id, str) and user_id:
                put_headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
                encoded_body = json.dumps({}).encode("utf-8")

                secret_response = http.request(
                    "PUT", f"http://localhost:8099/management/v1/users/{user_id}/secret", headers=put_headers, body=encoded_body
                )

                if secret_response.status < 400:
                    secret_data: Dict[str, Any] = json.loads(secret_response.data.decode("utf-8"))
                    client_id: Any = secret_data.get("clientId")
                    client_secret: Any = secret_data.get("clientSecret")

                    if isinstance(client_id, str) and client_id and isinstance(client_secret, str) and client_secret:
                        return {"client_id": client_id, "client_secret": client_secret}
                    else:
                        print(secret_data)  # noqa T201
                        raise ValueError("API response for secret is missing 'clientId' or 'clientSecret'.")
                else:
                    error_body = secret_response.data.decode("utf-8")
                    raise Exception(f"API call to generate secret failed for user ID: '{user_id}'. Response: {error_body}")
            else:
                print(user_response_map)  # noqa T201
                raise ValueError(f"Could not parse a valid user ID from API response for login name: '{login_name}'.")
        else:
            error_body = user_id_response.data.decode("utf-8")
            raise Exception(f"API call to retrieve user failed for login name: '{login_name}'. Response: {error_body}")

    def test_retrieves_general_settings_with_valid_client_credentials(self, docker_compose: Dict[str, str]) -> None:  # noqa F811
        """Retrieves general settings successfully with valid client credentials."""
        credentials = self.generate_user_secret(docker_compose["auth_token"])
        client = zitadel.Zitadel.with_client_credentials(
            docker_compose["base_url"],
            credentials["client_id"],
            credentials["client_secret"],
        )
        client.settings.settings_service_get_general_settings()

    def test_raises_api_exception_with_invalid_client_credentials(self, docker_compose: Dict[str, str]) -> None:  # noqa F811
        """Raises ApiException when using invalid client credentials."""
        client = zitadel.Zitadel.with_client_credentials(
            docker_compose["base_url"],
            "invalid",
            "invalid",
        )
        with pytest.raises(ZitadelError):
            client.settings.settings_service_get_general_settings()
