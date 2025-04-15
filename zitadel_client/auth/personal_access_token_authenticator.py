from typing import Dict

from zitadel_client.auth.authenticator import Authenticator
from zitadel_client.utils.url_util import URLUtil


class PersonalAccessTokenAuthenticator(Authenticator):
    """
    Personal Access Token Authenticator.

    Uses a static personal access token for API authentication.
    """

    def __init__(self, host: str, token: str):
        super().__init__(URLUtil.build_hostname(host))
        self.token = token

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Returns the authentication headers using the personal access token.

        :return: A dictionary containing the 'Authorization' header.
        """
        return {"Authorization": "Bearer " + self.token}
