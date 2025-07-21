import unittest

from zitadel_client.auth.no_auth_authenticator import NoAuthAuthenticator
from zitadel_client.configuration import Configuration


class ConfigurationTest(unittest.TestCase):
    def test_user_agent_getter_and_setter(self) -> None:
        """
        Test user agent getter and setter.

        @return void
        """
        config = Configuration(NoAuthAuthenticator())

        self.assertRegex(
            config.user_agent,
            r"^zitadel-client/\d+\.\d+\.\d+(-[a-zA-Z0-9]+(\.\d+)?)? \(lang=python; lang_version=[^;]+; os=[^;]+; arch=[^;]+\)$",
        )
        config.user_agent = "CustomUserAgent/1.0"
        self.assertEqual(config.user_agent, "CustomUserAgent/1.0")
