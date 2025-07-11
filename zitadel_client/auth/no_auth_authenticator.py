from typing import Dict

from zitadel_client.auth.authenticator import Authenticator


class NoAuthAuthenticator(Authenticator):
    """
    Dummy Authenticator for testing purposes.

    This authenticator does not apply any authentication to API requests.
    It simply returns an empty dictionary for authentication headers.
    """

    def __init__(self, host: str = "http://localhost", token: str = ""):
        """
        NoAuthAuthenticator constructor.

        Initializes the NoAuthAuthenticator with a default host and optional token.

        :param host: The base URL for the service. Defaults to "http://localhost".
        :param token: The token to be used for authentication. Defaults to an empty string.
        """
        super().__init__(host)
        self.token = token

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Retrieves the authentication token needed for API requests.

        Returns an empty dictionary since no authentication is performed.

        :return: An empty dictionary.
        """
        return {}

    def get_auth_token(self) -> str:
        """
        Retrieves the authentication token needed for API requests.

        :return: The authentication token.
        """
        return self.token
