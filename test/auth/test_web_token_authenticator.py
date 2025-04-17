import time
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

from test.auth.test_oauth_authenticator import OAuthAuthenticatorTest
from zitadel_client.auth.web_token_authenticator import WebTokenAuthenticator


class WebTokenAuthenticatorTest(OAuthAuthenticatorTest):
    """
    Test for WebTokenAuthenticator to verify JWT token refresh functionality using the builder.
    """

    def test_refresh_token_using_builder(self) -> None:
        time.sleep(20)

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        private_key_pem = key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption(),
        ).decode("utf-8")

        assert self.oauth_host is not None
        authenticator = (
            WebTokenAuthenticator.builder(
                self.oauth_host, "dummy-client", private_key_pem
            )
            .token_lifetime_seconds(3600)
            .build()
        )

        self.assertTrue(
            authenticator.get_auth_token(), "Access token should not be empty"
        )
        token = authenticator.refresh_token()
        self.assertEqual(
            {"Authorization": "Bearer " + token.access_token},
            authenticator.get_auth_headers(),
        )
        self.assertTrue(token.access_token, "Access token should not be null")
        self.assertTrue(
            token.expires_at > datetime.now(timezone.utc),
            "Token expiry should be in the future",
        )
        self.assertEqual(token.access_token, authenticator.get_auth_token())
        self.assertEqual(self.oauth_host, authenticator.get_host())
        self.assertNotEqual(
            authenticator.refresh_token().access_token,
            authenticator.refresh_token().access_token,
            "Two refreshToken calls should produce different tokens",
        )
