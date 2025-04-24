import os

import pytest

import zitadel_client as zitadel
from zitadel_client.exceptions import OpenApiError


@pytest.fixture(scope="module")
def base_url() -> str:
    """Provides the base URL for tests, skipping if unset."""
    url = os.getenv("BASE_URL")
    if not url:
        pytest.skip("Environment variable BASE_URL must be set", allow_module_level=True)
    return url


@pytest.fixture(scope="module")
def client_id() -> str:
    """Provides the client ID for tests, skipping if unset."""
    cid = os.getenv("CLIENT_ID")
    if not cid:
        pytest.skip("Environment variable CLIENT_ID must be set", allow_module_level=True)
    return cid


@pytest.fixture(scope="module")
def client_secret() -> str:
    """Provides the client secret for tests, skipping if unset."""
    cs = os.getenv("CLIENT_SECRET")
    if not cs:
        pytest.skip("Environment variable CLIENT_SECRET must be set", allow_module_level=True)
    return cs


class TestUseClientCredentialsSpec:
    """
    SettingsService Integration Tests (Client Credentials)

    This suite verifies the Zitadel SettingsService API's general settings
    endpoint works when authenticating via Client Credentials:

     1. Retrieve general settings successfully with valid credentials
     2. Expect an ApiException when using invalid credentials

    Each test instantiates a new client to ensure a clean, stateless call.
    """

    def test_retrieves_general_settings_with_valid_client_credentials(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        """Retrieves general settings successfully with valid client credentials."""
        client = zitadel.Zitadel.with_client_credentials(
            base_url,
            client_id,
            client_secret,
        )
        client.settings.settings_service_get_general_settings()

    def test_raises_api_exception_with_invalid_client_credentials(
        self,
        base_url: str,
    ) -> None:
        """Raises ApiException when using invalid client credentials."""
        client = zitadel.Zitadel.with_client_credentials(
            base_url,
            "invalid",
            "invalid",
        )
        with pytest.raises(OpenApiError):
            client.settings.settings_service_get_general_settings()
