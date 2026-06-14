from typing import Dict

import pytest

from spec.base_spec import docker_compose as docker_compose
from zitadel_client.errors import OpenApiException
from zitadel_client.zitadel import Zitadel


class TestUsePrivateKeySpec:
    """
    SettingsService Integration Tests (Private Key Assertion)

    This suite verifies the Zitadel SettingsService API's general settings
    endpoint works when authenticating via a private key assertion:

     1. Retrieve general settings successfully with a valid private key
     2. Expect an ApiException when using an invalid private key path

    Each test instantiates a new client to ensure a clean, stateless call.
    """

    async def test_retrieves_general_settings_with_valid_private_key(
        self, docker_compose: Dict[str, str]
    ) -> None:  # noqa F811
        """Retrieves general settings successfully with a valid private key."""
        client = Zitadel.with_private_key(
            docker_compose["base_url"],
            docker_compose["jwt_key"],
        )
        await client.settings.get_general_settings({})

    async def test_raises_api_exception_with_invalid_private_key(
        self, docker_compose: Dict[str, str]
    ) -> None:  # noqa F811
        """Raises ApiException when using an invalid private key path."""
        client = Zitadel.with_private_key(
            "https://zitadel.cloud",
            docker_compose["jwt_key"],
        )
        with pytest.raises(OpenApiException):
            await client.settings.get_general_settings({})
