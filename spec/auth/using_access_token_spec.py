from typing import Dict

import pytest

import zitadel_client as zitadel
from spec.base_spec import docker_compose as docker_compose
from zitadel_client.exceptions import ZitadelError


class TestUseAccessTokenSpec:
    """
    SettingsService Integration Tests (Personal Access Token)

    This suite verifies the Zitadel SettingsService API's general settings
    endpoint works when authenticating via a Personal Access Token:

     1. Retrieve general settings successfully with a valid token
     2. Expect an ApiException when using an invalid token

    Each test instantiates a new client to ensure a clean, stateless call.
    """

    def test_retrieves_general_settings_with_valid_token(self, docker_compose: Dict[str, str]) -> None:  # noqa F811
        """Retrieves general settings successfully with a valid access token."""
        client = zitadel.Zitadel.with_access_token(
            docker_compose["base_url"],
            docker_compose["auth_token"],
        )
        client.settings.get_general_settings()

    def test_raises_api_exception_with_invalid_token(self, docker_compose: Dict[str, str]) -> None:  # noqa F811
        """Raises ApiException when using an invalid access token."""
        client = zitadel.Zitadel.with_access_token(
            docker_compose["base_url"],
            "invalid",
        )
        with pytest.raises(ZitadelError):
            client.settings.get_general_settings()
