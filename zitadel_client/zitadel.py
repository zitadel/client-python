from types import TracebackType
from typing import Callable, Optional, Type, TypeVar

from zitadel_client.api import ActionServiceApi, SAMLServiceApi, WebKeyServiceApi
from zitadel_client.api.feature_service_api import FeatureServiceApi
from zitadel_client.api.identity_provider_service_api import IdentityProviderServiceApi
from zitadel_client.api.oidc_service_api import OIDCServiceApi
from zitadel_client.api.organization_service_api import OrganizationServiceApi
from zitadel_client.api.session_service_api import SessionServiceApi
from zitadel_client.api.settings_service_api import SettingsServiceApi
from zitadel_client.api.user_service_api import UserServiceApi
from zitadel_client.api_client import ApiClient
from zitadel_client.auth.authenticator import Authenticator
from zitadel_client.auth.client_credentials_authenticator import ClientCredentialsAuthenticator
from zitadel_client.auth.personal_access_token_authenticator import PersonalAccessTokenAuthenticator
from zitadel_client.auth.web_token_authenticator import WebTokenAuthenticator
from zitadel_client.configuration import Configuration


class Zitadel:
    """
    Main entry point for the Zitadel SDK.

    This class initializes and configures the SDK with the provided authentication strategy.
    It sets up service APIs for interacting with various Zitadel features such as identity providers,
    organizations, sessions, settings, users, and more.

    Attributes:
        configuration (Configuration): The configuration instance containing authentication and endpoint details.
        actions (ActionServiceApi): Service API for actions management.
        features (FeatureServiceApi): Service API for feature management.
        idps (IdentityProviderServiceApi): Service API for identity provider operations.
        oidc (OIDCServiceApi): Service API for OIDC-related operations.
        organizations (OrganizationServiceApi): Service API for organization-related operations.
        saml (SAMLServiceApi): Service API for SAML management.
        sessions (SessionServiceApi): Service API for session management.
        settings (SettingsServiceApi): Service API for settings management.
        users (UserServiceApi): Service API for user management.
        webkeys (WebKeyServiceApi): Service API for webkeys management.
    """

    def __init__(
        self,
        authenticator: Authenticator,
        mutate_config: Optional[Callable[[Configuration], None]] = None,
    ):
        """
        Initialize the Zitadel SDK.

        This constructor creates a configuration instance using the provided authenticator.
        Optionally, the configuration can be modified via the `mutate_config` callback function.
        It then instantiates the underlying API client and initializes various service APIs.

        Args:
            authenticator (Authenticator): The authentication strategy to be used.
            mutate_config (callable, optional): A callback function that receives the configuration
                instance for any additional modifications before the API client is created.
                Defaults to None.
        """
        self.configuration = Configuration(authenticator)

        if mutate_config:
            mutate_config(self.configuration)

        client = ApiClient(configuration=self.configuration)
        self.actions = ActionServiceApi(client)
        self.features = FeatureServiceApi(client)
        self.idps = IdentityProviderServiceApi(client)
        self.oidc = OIDCServiceApi(client)
        self.organizations = OrganizationServiceApi(client)
        self.saml = SAMLServiceApi(client)
        self.sessions = SessionServiceApi(client)
        self.settings = SettingsServiceApi(client)
        self.users = UserServiceApi(client)
        self.users = UserServiceApi(client)
        self.webkeys = WebKeyServiceApi(client)

    T = TypeVar("T", bound="Zitadel")

    def __enter__(self: T) -> T:
        """
        Enter the runtime context related to the Zitadel instance.

        Returns:
            Zitadel: The current instance.
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """
        Exit the runtime context.

        This method can be used to perform cleanup actions. Currently, it does nothing.

        Args:
            exc_type: The exception type, if an exception occurred.
            exc_value: The exception value, if an exception occurred.
            traceback: The traceback of the exception, if an exception occurred.
        """
        pass

    @staticmethod
    def with_access_token(host: str, access_token: str) -> "Zitadel":
        """
        Initialize the SDK with a Personal Access Token (PAT).

        :param host: API URL (e.g., "https://api.zitadel.example.com").
        :param access_token: Personal Access Token for Bearer authentication.
        :return: Configured Zitadel client instance.
        :see: https://zitadel.com/docs/guides/integrate/service-users/personal-access-token
        """
        return Zitadel(PersonalAccessTokenAuthenticator(host, access_token))

    @staticmethod
    def with_client_credentials(host: str, client_id: str, client_secret: str) -> "Zitadel":
        """
        Initialize the SDK using OAuth2 Client Credentials flow.

        :param host: API URL.
        :param client_id: OAuth2 client identifier.
        :param client_secret: OAuth2 client secret.
        :return: Configured Zitadel client instance with token auto-refresh.
        :see: https://zitadel.com/docs/guides/integrate/service-users/client-credentials
        """
        return Zitadel(ClientCredentialsAuthenticator.builder(host, client_id, client_secret).build())

    @staticmethod
    def with_private_key(host: str, key_file: str) -> "Zitadel":
        """
        Initialize the SDK via Private Key JWT assertion.

        :param host: API URL.
        :param key_file: Path to service account JSON or PEM key file.
        :return: Configured Zitadel client instance using JWT assertion.
        :see: https://zitadel.com/docs/guides/integrate/service-users/private-key-jwt
        """
        return Zitadel(WebTokenAuthenticator.from_json(host, key_file))
