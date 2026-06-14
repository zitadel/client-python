from test.auth.test_oauth_authenticator import OAuthAuthenticatorTest
from zitadel_client.auth.client_credentials_authenticator import (
    ClientCredentialsAuthenticator,
)


class ClientCredentialsAuthenticatorTest(OAuthAuthenticatorTest):
    """
    Test for ClientCredentialsAuthenticator to verify token refresh functionality.
    Extends the base OAuthAuthenticatorTest class.
    """

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
