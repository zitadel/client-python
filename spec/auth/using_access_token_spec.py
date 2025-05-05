import os

import pytest

import zitadel_client as zitadel
from zitadel_client.exceptions import ZitadelError


@pytest.fixture(scope="module")
def base_url() -> str:
    """Provides the base URL for tests, skipping if unset."""
    url = os.getenv("BASE_URL")
    if not url:
        pytest.skip("Environment variable BASE_URL must be set", allow_module_level=True)
    return url


@pytest.fixture(scope="module")
def auth_token() -> str:
    """Provides the auth token for tests, skipping if unset."""
    url = os.getenv("AUTH_TOKEN")
    if not url:
        pytest.skip("Environment variable AUTH_TOKEN must be set", allow_module_level=True)
    return url


class TestUseAccessTokenSpec:
    """
    SettingsService Integration Tests (Personal Access Token)

    This suite verifies the Zitadel SettingsService API's general settings
    endpoint works when authenticating via a Personal Access Token:

     1. Retrieve general settings successfully with a valid token
     2. Expect an ApiException when using an invalid token

    Each test instantiates a new client to ensure a clean, stateless call.
    """

    def test_retrieves_general_settings_with_valid_token(
        self,
        base_url: str,
        auth_token: str,
    ) -> None:
        """Retrieves general settings successfully with a valid access token."""
        client = zitadel.Zitadel.with_access_token(
            base_url,
            auth_token,
        )
        client.settings.settings_service_get_general_settings()

    def test_raises_api_exception_with_invalid_token(
        self,
        base_url: str,
    ) -> None:
        """Raises ApiException when using an invalid access token."""
        client = zitadel.Zitadel.with_access_token(
            base_url,
            "invalid",
        )
        with pytest.raises(ZitadelError):
            client.settings.settings_service_get_general_settings()
