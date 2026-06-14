from typing import Dict, Optional, Set

from zitadel_client.auth.oauth_authenticator import (
    OAuthAuthenticator,
    OAuthAuthenticatorBuilder,
)
from zitadel_client.auth.open_id import OpenId
from zitadel_client.transport_options import TransportOptions


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
        auth_scopes: Set[str],
    ):
        """
        Constructs a ClientCredentialsAuthenticator.

        :param open_id: Resolved OpenID configuration for the provider.
        :param client_id: The OAuth client identifier.
        :param client_secret: The OAuth client secret.
        :param auth_scopes: The scope(s) for the token request.
        """
        super().__init__(open_id, client_id, " ".join(auth_scopes))
        self.client_secret = client_secret

    def get_grant_type(self) -> str:
        return self.GRANT_TYPE

    def get_access_token_options(self) -> Dict[str, str]:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }

    @staticmethod
    def builder(
        host: str,
        client_id: str,
        client_secret: str,
        transport_options: Optional[TransportOptions] = None,
    ) -> "ClientCredentialsAuthenticatorBuilder":
        """
        Returns a builder for constructing a ClientCredentialsAuthenticator.

        :param host: The base URL for the OAuth provider.
        :param client_id: The OAuth client identifier.
        :param client_secret: The OAuth client secret.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        :return: A ClientCredentialsAuthenticatorBuilder instance.
        """
        return ClientCredentialsAuthenticatorBuilder(
            host, client_id, client_secret, transport_options=transport_options
        )


class ClientCredentialsAuthenticatorBuilder(
    OAuthAuthenticatorBuilder["ClientCredentialsAuthenticatorBuilder"]
):
    """
    Builder class for constructing ClientCredentialsAuthenticator instances.

    Extends the base OAuthAuthenticatorBuilder with the client_id and
    client_secret required for the client-credentials flow.
    """

    def __init__(
        self,
        host: str,
        client_id: str,
        client_secret: str,
        transport_options: Optional[TransportOptions] = None,
    ):
        """
        Initializes the ClientCredentialsAuthenticatorBuilder.

        :param host: The base URL for the OAuth provider.
        :param client_id: The OAuth client identifier.
        :param client_secret: The OAuth client secret.
        :param transport_options: Optional transport options for TLS, proxy, and headers.
        """
        super().__init__(host, transport_options=transport_options)
        self.client_id = client_id
        self.client_secret = client_secret

    def build(self) -> ClientCredentialsAuthenticator:
        """
        Constructs and returns a ClientCredentialsAuthenticator instance.

        :return: A configured ClientCredentialsAuthenticator.
        """
        return ClientCredentialsAuthenticator(
            self.open_id,
            self.client_id,
            self.client_secret,
            self.auth_scopes,
        )
