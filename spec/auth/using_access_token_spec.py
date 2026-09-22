from typing import Dict

import pytest

from spec.base_spec import docker_compose as docker_compose
from zitadel_client.auth.personal_access_token_authenticator import (
    PersonalAccessTokenAuthenticator,
)
from zitadel_client.errors.unauthorized_exception import UnauthorizedException
from zitadel_client.zitadel import Zitadel


class TestUseAccessTokenSpec:
    """
    SettingsService Integration Tests (Personal Access Token)

    This suite verifies the Zitadel SettingsService API's general settings
    endpoint works when authenticating via a Personal Access Token:

     1. Retrieve general settings successfully with a valid token
     2. Expect an UnauthorizedException when using an invalid token

    Each test instantiates a new client to ensure a clean, stateless call.
    """

    async def test_retrieves_general_settings_with_valid_token(
        self, docker_compose: Dict[str, str]
    ) -> None:  # noqa F811
        """Retrieves general settings successfully with a valid access token."""
        client = Zitadel.with_authenticator(
            PersonalAccessTokenAuthenticator(
                docker_compose["base_url"],
                docker_compose["auth_token"],
            )
        )
        await client.settings_service.get_general_settings({})

    async def test_raises_api_exception_with_invalid_token(
        self, docker_compose: Dict[str, str]
    ) -> None:  # noqa F811
        """Raises UnauthorizedException when using an invalid access token."""
        client = Zitadel.with_authenticator(
            PersonalAccessTokenAuthenticator(
                docker_compose["base_url"],
                "invalid",
            )
        )
        with pytest.raises(UnauthorizedException) as excinfo:
            await client.settings_service.get_general_settings({})
        assert type(excinfo.value) is UnauthorizedException
