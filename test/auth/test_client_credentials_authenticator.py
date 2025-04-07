import time
from datetime import datetime, timezone

from test.auth.test_oauth_authenticator import OAuthAuthenticatorTest
from zitadel_client.auth.client_credentials_authenticator import ClientCredentialsAuthenticator


class ClientCredentialsAuthenticatorTest(OAuthAuthenticatorTest):
  """
  Test for ClientCredentialsAuthenticator to verify token refresh functionality.
  Extends the base OAuthAuthenticatorTest class.
  """

  def test_refresh_token(self):
    time.sleep(20)

    authenticator = ClientCredentialsAuthenticator.builder(self.oauth_host, "dummy-client", "dummy-secret") \
      .scopes("openid", "foo") \
      .build()

    self.assertTrue(authenticator.get_auth_token(), "Access token should not be empty")
    token = authenticator.refresh_token()
    self.assertEqual({"Authorization": "Bearer " + token.access_token}, authenticator.get_auth_headers())
    self.assertTrue(token.access_token, "Access token should not be null")
    self.assertTrue(token.expires_at > datetime.now(timezone.utc), "Token expiry should be in the future")
    self.assertEqual(token.access_token, authenticator.get_auth_token())
    self.assertEqual(self.oauth_host, authenticator.get_host())
    self.assertNotEqual(authenticator.refresh_token().access_token, authenticator.refresh_token().access_token,
                        "Two refreshToken calls should produce different tokens")
