from unittest.mock import Mock

from test.auth.test_oauth_authenticator import OAuthAuthenticatorTest
from zitadel_client.auth.client_credentials_authenticator import (
    ClientCredentialsAuthenticator,
)
from zitadel_client.auth.open_id import OpenId


class ClientCredentialsAuthenticatorTest(OAuthAuthenticatorTest):
    """
    Test for ClientCredentialsAuthenticator to verify token refresh functionality.
    Extends the base OAuthAuthenticatorTest class.
    """

    def test_redacts_secret_in_repr(self) -> None:
        """The client secret is masked in repr while the client id stays visible."""
        secret = "super-secret-value-9000"
        open_id = Mock(spec=OpenId)
        open_id.get_host_endpoint.return_value = "https://example.zitadel.cloud"
        authenticator = ClientCredentialsAuthenticator(
            open_id, "client-1", secret, {"openid"}
        )

        rendered = repr(authenticator)

        self.assertNotIn(secret, rendered)
        self.assertIn("***", rendered)
        self.assertIn("client-1", rendered)

    # noinspection DuplicatedCode
    def test_refresh_token(self) -> None:

        assert self.oauth_host is not None
        authenticator = self.inject_api_client(
            ClientCredentialsAuthenticator.builder(
                self.oauth_host, "dummy-client", "dummy-secret"
            )
            .scopes("openid", "foo")
            .build()
        )

        self.assertTrue(
            authenticator.get_auth_token(), "Access token should not be empty"
        )
        token = authenticator.refresh_token()
        self.assertEqual(
            {"Authorization": "Bearer " + token},
            authenticator.get_auth_headers(),
        )
        self.assertTrue(token, "Access token should not be null")
        self.assertEqual(token, authenticator.get_auth_token())
        self.assertEqual(self.oauth_host, authenticator.get_host())
        self.assertNotEqual(
            authenticator.refresh_token(),
            authenticator.refresh_token(),
            "Two refreshToken calls should produce different tokens",
        )
