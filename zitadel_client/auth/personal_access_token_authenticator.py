from typing import Dict

from zitadel_client.auth.base_authenticator import BaseAuthenticator


class PersonalAccessTokenAuthenticator(BaseAuthenticator):
    """
    Personal Access Token Authenticator.

    Uses a static personal access token (PAT) for API authentication. A PAT is
    a long-lived bearer credential minted out-of-band in the Zitadel console,
    so no token exchange is required: the token is attached verbatim on every
    request. This authenticator therefore implements :class:`Authenticator`
    directly (via :class:`BaseAuthenticator`) and does NOT need
    :class:`HttpAwareAuthenticator`.
    """

    def __init__(self, host: str, token: str):
        """
        Constructs a PersonalAccessTokenAuthenticator.

        :param host: The base URL for the API endpoints.
        :param token: The personal access token.
        """
        self.host = self._build_hostname(host)
        self.token = token

    @staticmethod
    def _build_hostname(host: str) -> str:
        host = host.strip()
        # noinspection HttpUrlsUsage
        if not host.startswith("http://") and not host.startswith("https://"):
            host = "https://" + host
        return host

    def get_host(self) -> str:
        return self.host

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Returns the authentication headers using the personal access token.

        :return: A dictionary containing the 'Authorization' header.
        """
        return {"Authorization": "Bearer " + self.token}

    def __repr__(self) -> str:
        # Mask the token so it never leaks through repr() / logging.
        return f"{type(self).__name__}(host={self.host!r}, token='***')"
