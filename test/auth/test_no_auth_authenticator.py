import unittest

from zitadel_client.auth.no_auth_authenticator import NoAuthAuthenticator


class NoAuthAuthenticatorTest(unittest.TestCase):
  def test_returns_empty_headers_and_default_host(self):
    auth = NoAuthAuthenticator()
    self.assertEqual({}, auth.get_auth_headers())
    self.assertEqual("http://localhost", auth.get_host())

  def test_returns_empty_headers_and_custom_host(self):
    auth = NoAuthAuthenticator("https://custom-host")
    self.assertEqual({}, auth.get_auth_headers())
    self.assertEqual("https://custom-host", auth.get_host())
