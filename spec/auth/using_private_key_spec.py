from typing import Dict

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from spec.base_spec import docker_compose as docker_compose
from zitadel_client.auth.web_token_authenticator import WebTokenAuthenticator
from zitadel_client.errors.oauth2_server_exception import OAuth2ServerException
from zitadel_client.zitadel import Zitadel


class TestUsePrivateKeySpec:
    """
    SettingsService Integration Tests (Private Key Assertion)

    This suite verifies the Zitadel SettingsService API's general settings
    endpoint works when authenticating via a private key assertion:

     1. Retrieve general settings successfully with a valid private key
     2. Expect an OAuth2ServerException when signing with an unknown key

    Each test instantiates a new client to ensure a clean, stateless call.
    """

    async def test_retrieves_general_settings_with_valid_private_key(
        self, docker_compose: Dict[str, str]
    ) -> None:  # noqa F811
        """Retrieves general settings successfully with a valid private key."""
        client = Zitadel.with_authenticator(
            WebTokenAuthenticator.from_json(
                docker_compose["base_url"],
                docker_compose["jwt_key"],
            )
        )
        await client.settings_service.get_general_settings({})

    async def test_raises_api_exception_with_invalid_private_key(
        self, docker_compose: Dict[str, str]
    ) -> None:  # noqa F811
        """Raises OAuth2ServerException when signing with a key the instance does not know."""
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem = key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        ).decode("utf-8")
        client = Zitadel.with_authenticator(
            WebTokenAuthenticator.builder(docker_compose["base_url"], "invalid", pem)
            .key_id("invalid")
            .build()
        )
        with pytest.raises(OAuth2ServerException) as excinfo:
            await client.settings_service.get_general_settings({})
        assert type(excinfo.value) is OAuth2ServerException
