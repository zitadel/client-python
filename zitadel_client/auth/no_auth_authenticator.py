from typing import Dict

from zitadel_client.auth.authenticator import Authenticator


class NoAuthAuthenticator(Authenticator):
    """
    A simple authenticator that performs no authentication.

    This authenticator is useful for cases where no token or credentials are required.
    It simply returns an empty dictionary for authentication headers.
    """

    def __init__(self, host: str = "http://localhost"):
        """
        Initializes the NoAuthAuthenticator with a default host.

        :param host: The base URL for the service. Defaults to "http://localhost".
        """
        super().__init__(host)

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Returns an empty dictionary since no authentication is performed.

        :return: An empty dictionary.
        """
        return {}
