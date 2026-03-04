import sys
from typing import Dict, Optional, Set

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from authlib.integrations.requests_client import OAuth2Session

from zitadel_client.auth.oauth_authenticator import (
    OAuthAuthenticator,
    OAuthAuthenticatorBuilder,
)
from zitadel_client.auth.open_id import OpenId
from zitadel_client.transport_options import TransportOptions


class ClientCredentialsAuthenticator(OAuthAuthenticator):
    """
    OAuth authenticator implementing the client credentials flow.

    Uses client_id and client_secret to obtain an access token from the OAuth2 token endpoint.
    """

    def __init__(
        self,
        open_id: OpenId,
        client_id: str,
        client_secret: str,
        auth_scopes: Set[str],
        transport_options: Optional[TransportOptions] = None,
    ):
        """
        Constructs a ClientCredentialsAuthenticator.

        :param open_id: The base URL for the OAuth provider.
        :param client_id: The OAuth client identifier.
        :param client_secret: The OAuth client secret.
        :param auth_scopes: The scope(s) for the token request.
        :param transport_options: Optional TransportOptions for configuring HTTP connections.
        """
        opts = transport_options or TransportOptions.defaults()

        session = OAuth2Session(
            client_id=client_id,
            client_secret=client_secret,
            scope=" ".join(auth_scopes),
            **opts.to_session_kwargs(),
        )

        if opts.default_headers:
            session.headers.update(opts.default_headers)

        super().__init__(
            open_id,
            session,
            transport_options=opts,
        )

    @override
    def get_grant(self) -> Dict[str, str]:
        """
        Returns the grant parameters for the client credentials flow.

        :return: A dictionary with the grant type for client credentials.
        """
        return {"grant_type": "client_credentials"}

    @staticmethod
    def builder(
        host: str, client_id: str, client_secret: str, transport_options: Optional[TransportOptions] = None
    ) -> "ClientCredentialsAuthenticatorBuilder":
        """
        Returns a builder for constructing a ClientCredentialsAuthenticator.

        :param host: The base URL for the OAuth provider.
        :param client_id: The OAuth client identifier.
        :param client_secret: The OAuth client secret.
        :param transport_options: Optional TransportOptions for configuring HTTP connections.
        :return: A ClientCredentialsAuthenticatorBuilder instance.
        """
        return ClientCredentialsAuthenticatorBuilder(host, client_id, client_secret, transport_options=transport_options)


class ClientCredentialsAuthenticatorBuilder(OAuthAuthenticatorBuilder["ClientCredentialsAuthenticatorBuilder"]):
    """
    Builder class for constructing ClientCredentialsAuthenticator instances.

    This builder extends the OAuthAuthenticatorBuilder with client credentials (client_id and client_secret)
    required for the client credentials flow.
    """

    def __init__(self, host: str, client_id: str, client_secret: str, transport_options: Optional[TransportOptions] = None):
        """
        Initializes the ClientCredentialsAuthenticatorBuilder with host, client ID, and client secret.

        :param host: The base URL for the OAuth provider.
        :param client_id: The OAuth client identifier.
        :param client_secret: The OAuth client secret.
        :param transport_options: Optional TransportOptions for configuring HTTP connections.
        """
        super().__init__(host, transport_options=transport_options)
        self.client_id = client_id
        self.client_secret = client_secret

    def build(self) -> ClientCredentialsAuthenticator:
        """
        Constructs and returns a ClientCredentialsAuthenticator instance using the configured parameters.

        :return: A configured ClientCredentialsAuthenticator.
        """
        return ClientCredentialsAuthenticator(
            self.open_id,
            self.client_id,
            self.client_secret,
            self.auth_scopes,
            transport_options=self.transport_options,
        )
