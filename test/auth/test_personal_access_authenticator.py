import unittest

from zitadel_client.auth.personal_access_token_authenticator import PersonalAccessTokenAuthenticator


class PersonalAccessTokenAuthenticatorTest(unittest.TestCase):
  def test_returns_expected_headers_and_host(self) -> None:
    auth = PersonalAccessTokenAuthenticator("https://api.example.com", "my-secret-token")
    self.assertEqual({"Authorization": "Bearer my-secret-token"}, auth.get_auth_headers())
    self.assertEqual("https://api.example.com", auth.get_host())
