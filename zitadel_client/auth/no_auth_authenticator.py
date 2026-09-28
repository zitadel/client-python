from typing import Dict

from zitadel_client.auth.base_authenticator import BaseAuthenticator
from zitadel_client.auth.open_id import OpenId


class NoAuthAuthenticator(BaseAuthenticator):
    """
    A no-op authenticator that performs no authentication.

    Useful for testing and unauthenticated endpoints: it never mints a token,
    so it returns an empty set of auth headers.
    """

    def __init__(self, host: str = "http://localhost"):
        """
        Initializes the NoAuthAuthenticator.

        :param host: The base URL for the API endpoints. Defaults to
            "http://localhost".
        :raises ValueError: If the host is not a valid http or https URL.
        """
        self.host = OpenId(host).get_host_endpoint()

    def get_host(self) -> str:
        return self.host

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Returns an empty dictionary since no authentication is performed.

        :return: An empty dictionary.
        """
        return {}
