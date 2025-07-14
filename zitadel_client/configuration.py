import platform

from zitadel_client.auth.authenticator import Authenticator
from zitadel_client.version import Version


class Configuration:
    """This class contains various settings of the API client."""

    def __init__(self, authenticator: Authenticator, timeout: int = 30, connect_timeout: int = 5) -> None:
        """Constructor"""
        self._user_agent = " ".join(
            [
                f"zitadel-client/{Version.VERSION}",
                "("
                + "; ".join(
                    [
                        "lang=python",
                        f"lang_version={platform.python_version()}",
                        f"os={platform.system()}",
                        f"arch={platform.machine()}",
                    ]
                )
                + ")",
            ]
        ).lower()
        self._authenticator = authenticator
        self._timeout = timeout
        self._connect_timeout = connect_timeout

    @property
    def host(self) -> str:
        """Return generated host."""
        return self._authenticator.get_host()

    @property
    def user_agent(self) -> str:
        """
        Get the user agent string.

        Returns:
            str: The current value of the user agent.
        """
        return self._user_agent

    @property
    def access_token(self) -> str:
        """
        Gets the authentication access token (Bearer Token).
        """
        return self._authenticator.get_auth_token()

    @property
    def timeout(self) -> int:
        """
        Gets the total request timeout in seconds.
        """
        return self._timeout

    @property
    def connect_timeout(self) -> int:
        """
        Gets the connection timeout in seconds.
        """
        return self._connect_timeout
