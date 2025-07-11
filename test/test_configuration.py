import unittest

from zitadel_client.auth.no_auth_authenticator import NoAuthAuthenticator
from zitadel_client.configuration import Configuration


class ConfigurationTest(unittest.TestCase):
    """
    OAuth host for testing.
    """

    # noinspection HttpUrlsUsage
    oauth_host = "http://zitadel.com"

    """
    Test user agent getter and setter.
    """

    def test_user_agent(self) -> None:
        authenticator = NoAuthAuthenticator(self.oauth_host, "test-token")
        config = Configuration(authenticator)

        self.assertTrue(
            config.user_agent.startswith("zitadel-client/")
            and "lang=python" in config.user_agent
            and "os=" in config.user_agent
            and "arch=" in config.user_agent
        )

    """
    Test getting access token.
    """

    def test_get_access_token(self) -> None:
        authenticator = NoAuthAuthenticator(self.oauth_host, "test-token")
        config = Configuration(authenticator)

        self.assertEqual("test-token", config.access_token)

    """
    Test getting host from authenticator.
    """

    def test_get_host(self) -> None:
        authenticator = NoAuthAuthenticator(self.oauth_host, "test-token")
        config = Configuration(authenticator)

        self.assertEqual(self.oauth_host, config.host)

    """
    Test connection timeout.
    """

    def test_get_connect_timeout(self) -> None:
        authenticator = NoAuthAuthenticator(self.oauth_host, "test-token")
        config = Configuration(authenticator)

        self.assertEqual(5, config.connect_timeout)

    """
    Test total timeout.
    """

    def test_get_timeout(self) -> None:
        authenticator = NoAuthAuthenticator(self.oauth_host, "test-token")
        config = Configuration(authenticator)

        self.assertEqual(30, config.timeout)
