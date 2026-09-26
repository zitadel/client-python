from typing import Dict

from zitadel_client.auth.oauth_authenticator import (
    OAuthAuthenticator,
    OAuthAuthenticatorBuilder,
    require_text,
)
from zitadel_client.auth.open_id import OpenId


class ClientCredentialsAuthenticator(OAuthAuthenticator):
    """
    OAuth authenticator implementing the client-credentials flow (RFC 6749 §4.4).

    Mints a bearer token by POSTing client_id / client_secret to the provider's
    token endpoint through the SDK's shared transport. See
    :class:`OAuthAuthenticator` for the caching and HTTP-injection contract.
    """

    GRANT_TYPE = "client_credentials"

    def __init__(
        self,
        open_id: OpenId,
        client_id: str,
        client_secret: str,
        scope: str,
    ):
        """
        Constructs a ClientCredentialsAuthenticator.

        :param open_id: The OpenID discovery helper for the target host.
        :param client_id: The OAuth client identifier.
        :param client_secret: The OAuth client secret.
        :param scope: Space-delimited scope string for the token request.
        """
        super().__init__(open_id, scope)
        self.client_id = client_id
        self.client_secret = client_secret

    def __repr__(self) -> str:
        """Redacts the client secret and cached token so they never leak into
        logs or tracebacks, while the client id stays visible."""
        return (
            f"{type(self).__name__}(host={self.get_host()!r}, "
            f"client_id={self.client_id!r}, client_secret='***', "
            f"scope={self.scope!r}, access_token={self._masked_token()!r})"
        )

    def get_grant_type(self) -> str:
        return self.GRANT_TYPE

    def get_token_request_params(self) -> Dict[str, str]:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

    @staticmethod
    def builder(
        host: str, client_id: str, client_secret: str
    ) -> "ClientCredentialsAuthenticatorBuilder":
        """
        Returns a builder for constructing a ClientCredentialsAuthenticator.

        :param host: The base URL for the OAuth provider.
        :param client_id: The OAuth client identifier.
        :param client_secret: The OAuth client secret.
        :return: A ClientCredentialsAuthenticatorBuilder instance.
        :raises ValueError: If the host is not a valid http or https URL, or
            the client identifier or secret is empty.
        """
        return ClientCredentialsAuthenticatorBuilder(host, client_id, client_secret)


class ClientCredentialsAuthenticatorBuilder(
    OAuthAuthenticatorBuilder["ClientCredentialsAuthenticatorBuilder"]
):
    """
    Builder class for constructing ClientCredentialsAuthenticator instances.
    """

    def __init__(self, host: str, client_id: str, client_secret: str):
        """
        Initializes the ClientCredentialsAuthenticatorBuilder.

        :param host: The base URL for the OAuth provider.
        :param client_id: The OAuth client identifier.
        :param client_secret: The OAuth client secret.
        """
        super().__init__(host)
        self.client_id = require_text(client_id, "Client ID")
        self.client_secret = require_text(client_secret, "Client secret")

    def build(self) -> ClientCredentialsAuthenticator:
        """
        Constructs and returns a ClientCredentialsAuthenticator instance.

        :return: A configured ClientCredentialsAuthenticator.
        """
        return ClientCredentialsAuthenticator(
            self.open_id, self.client_id, self.client_secret, self.scope
        )
