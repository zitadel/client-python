from typing import Dict

from zitadel_client.auth.base_authenticator import BaseAuthenticator


class NoAuthAuthenticator(BaseAuthenticator):
    """
    A no-op authenticator that performs no authentication.

    Useful for testing and unauthenticated endpoints: it has no host-dependent
    state and never mints a token, so it returns an empty set of auth headers.
    """

    def __init__(self, host: str = "http://localhost"):
        """
        Initializes the NoAuthAuthenticator with a default host.

        :param host: The base URL for the service. Defaults to "http://localhost".
        """
        self.host = host

    def get_host(self) -> str:
        return self.host

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Returns an empty dictionary since no authentication is performed.

        :return: An empty dictionary.
        """
        return {}
